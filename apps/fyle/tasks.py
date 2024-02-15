import logging
import traceback
from datetime import datetime
from typing import Dict, List

from django.db import transaction
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.actions import create_generator_and_post_in_batches
from apps.fyle.enums import ExpenseStateEnum, FundSourceEnum, PlatformExpensesEnum
from apps.fyle.helpers import get_filter_credit_expenses, get_fund_source, get_source_account_type, handle_import_exception
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.queue import async_post_accounting_export_summary
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import TaskLog
from apps.workspaces.actions import export_to_xero
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO


SOURCE_ACCOUNT_MAP = {
    FundSourceEnum.PERSONAL: PlatformExpensesEnum.PERSONAL_CASH_ACCOUNT,
    FundSourceEnum.CCC: PlatformExpensesEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT
}


def get_task_log_and_fund_source(workspace_id: int):
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type=TaskLogTypeEnum.FETCHING_EXPENSES,
        defaults={"status": TaskLogStatusEnum.IN_PROGRESS},
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append(FundSourceEnum.PERSONAL)
    if general_settings.corporate_credit_card_expenses_object is not None:
        fund_source.append(FundSourceEnum.CCC)

    return task_log, fund_source


def create_expense_groups(workspace_id: int, fund_source: List[str], task_log: TaskLog):
    """
    Create expense groups
    :param task_log: Task log object
    :param workspace_id: workspace id
    :param state: expense state
    :param fund_source: expense fund source
    :return: task log
    """

    async_create_expense_groups(workspace_id, fund_source, task_log)

    task_log.detail = {"message": "Creating expense groups"}
    task_log.save()

    return task_log


def async_create_expense_groups(
    workspace_id: int, fund_source: List[str], task_log: TaskLog
):
    try:
        with transaction.atomic():
            expense_group_settings = ExpenseGroupSettings.objects.get(
                workspace_id=workspace_id
            )
            workspace = Workspace.objects.get(pk=workspace_id)
            last_synced_at = workspace.last_synced_at
            ccc_last_synced_at = workspace.ccc_last_synced_at
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials)

            filter_credit_expenses = True
            if expense_group_settings.import_card_credits:
                filter_credit_expenses = False

            expenses = []
            reimbursable_expenses_count = 0

            if FundSourceEnum.PERSONAL in fund_source:
                expenses.extend(
                    platform.expenses.get(
                        source_account_type=[SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL]],
                        state=expense_group_settings.reimbursable_expense_state,
                        settled_at=last_synced_at
                        if expense_group_settings.reimbursable_expense_state
                        == ExpenseStateEnum.PAYMENT_PROCESSING
                        else None,
                        filter_credit_expenses=True,
                        last_paid_at=last_synced_at
                        if expense_group_settings.reimbursable_expense_state == ExpenseStateEnum.PAID
                        else None,
                    )
                )

            if expenses:
                workspace.last_synced_at = datetime.now()
                reimbursable_expenses_count += len(expenses)

            if FundSourceEnum.CCC in fund_source:
                expenses.extend(
                    platform.expenses.get(
                        source_account_type=[SOURCE_ACCOUNT_MAP[FundSourceEnum.CCC]],
                        state=expense_group_settings.ccc_expense_state,
                        settled_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state
                        == ExpenseStateEnum.PAYMENT_PROCESSING
                        else None,
                        approved_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state == ExpenseStateEnum.APPROVED
                        else None,
                        filter_credit_expenses=filter_credit_expenses,
                        last_paid_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state == ExpenseStateEnum.PAID
                        else None,
                    )
                )

            if len(expenses) != reimbursable_expenses_count:
                workspace.ccc_last_synced_at = datetime.now()

            workspace.save()

            expense_objects = Expense.create_expense_objects(expenses, workspace_id)

            ExpenseGroup.create_expense_groups_by_report_id_fund_source(
                expense_objects, workspace_id
            )

            task_log.status = TaskLogStatusEnum.COMPLETE

            task_log.save()

    except FyleCredential.DoesNotExist:
        logger.info("Fyle credentials not found %s", workspace_id)
        task_log.detail = {"message": "Fyle credentials do not exist in workspace"}
        task_log.status = TaskLogStatusEnum.FAILED
        task_log.save()

    except FyleInvalidTokenError:
        logger.info("Invalid Token for Fyle")
    except Exception:
        error = traceback.format_exc()
        task_log.detail = {"error": error}
        task_log.status = TaskLogStatusEnum.FATAL
        task_log.save()
        logger.exception(
            "Something unexpected happened workspace_id: %s %s",
            task_log.workspace_id,
            task_log.detail,
        )


def sync_dimensions(fyle_credentials):
    platform = PlatformConnector(fyle_credentials)
    platform.import_fyle_dimensions()


def group_expenses_and_save(expenses: List[Dict], task_log: TaskLog, workspace: Workspace):
    expense_objects = Expense.create_expense_objects(expenses, workspace.id)
    configuration: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace.id)
    filtered_expenses = expense_objects
    expenses_object_ids = [expense_object.id for expense_object in expense_objects]

    async_post_accounting_export_summary(workspace.fyle_org_id, workspace.id)

    filtered_expenses = Expense.objects.filter(
        id__in=expenses_object_ids,
        expensegroup__isnull=True,
        org_id=workspace.fyle_org_id
    )

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        filtered_expenses, configuration, workspace.id
    )

    task_log.status = 'COMPLETE'
    task_log.save()


def import_and_export_expenses(report_id: str, org_id: str) -> None:
    """
    Import and export expenses
    :param report_id: report id
    :param org_id: org id
    :return: None
    """
    workspace = Workspace.objects.get(fyle_org_id=org_id)
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace.id)

    try:
        with transaction.atomic():
            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

            fund_source = get_fund_source(workspace.id)
            source_account_type = get_source_account_type(fund_source)
            filter_credit_expenses = get_filter_credit_expenses(expense_group_settings)

            platform = PlatformConnector(fyle_credentials)
            expenses = platform.expenses.get(
                source_account_type,
                filter_credit_expenses=filter_credit_expenses,
                report_id=report_id
            )

            group_expenses_and_save(expenses, task_log, workspace)

        # Export only selected expense groups
        expense_ids = Expense.objects.filter(report_id=report_id, org_id=org_id).values_list('id', flat=True)
        expense_groups = ExpenseGroup.objects.filter(expenses__id__in=[expense_ids], workspace_id=workspace.id).distinct('id').values('id')
        expense_group_ids = [expense_group['id'] for expense_group in expense_groups]

        if len(expense_group_ids):
            export_to_xero(workspace.id, None, expense_group_ids)

    except Exception:
        handle_import_exception(task_log)


def post_accounting_export_summary(org_id: str, workspace_id: int, fund_source: str = None) -> None:
    """
    Post accounting export summary to Fyle
    :param org_id: org id
    :param workspace_id: workspace id
    :param fund_source: fund source
    :return: None
    """
    # Iterate through all expenses which are not synced and post accounting export summary to Fyle in batches
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    filters = {
        'org_id': org_id,
        'accounting_export_summary__synced': False
    }

    if fund_source:
        filters['fund_source'] = fund_source

    expenses_count = Expense.objects.filter(**filters).count()

    accounting_export_summary_batches = []
    page_size = 200
    for offset in range(0, expenses_count, page_size):
        limit = offset + page_size
        paginated_expenses = Expense.objects.filter(**filters).order_by('id')[offset:limit]

        payload = []

        for expense in paginated_expenses:
            accounting_export_summary = expense.accounting_export_summary
            accounting_export_summary.pop('synced')
            payload.append(expense.accounting_export_summary)

        accounting_export_summary_batches.append(payload)

    logger.info(
        'Posting accounting export summary to Fyle workspace_id: %s, payload: %s',
        workspace_id,
        accounting_export_summary_batches
    )
    create_generator_and_post_in_batches(accounting_export_summary_batches, platform, workspace_id)
