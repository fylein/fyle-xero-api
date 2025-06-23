import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List

from django.db.models import Q
from django.db import transaction
from apps.fyle.actions import mark_expenses_as_skipped, post_accounting_export_summary
from fyle.platform.exceptions import InternalServerError
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle.platform.exceptions import RetryException
from fyle_accounting_library.fyle_platform.branding import feature_configuration
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_library.fyle_platform.helpers import filter_expenses_based_on_state, get_expense_import_states
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_integrations_platform_connector import PlatformConnector
from fyle_integrations_platform_connector.apis.expenses import Expenses as FyleExpenses

from apps.fyle.enums import ExpenseStateEnum, FundSourceEnum, PlatformExpensesEnum
from apps.fyle.helpers import (
    get_filter_credit_expenses,
    get_fund_source,
    get_source_account_type,
    handle_import_exception,
    update_task_log_post_import,
)
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import TaskLog
from apps.workspaces.actions import export_to_xero
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings, WorkspaceSchedule

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


def create_expense_groups(
    workspace_id: int, fund_source: List[str], task_log: TaskLog | None, imported_from: ExpenseImportSourceEnum
):
    try:
        with transaction.atomic():
            expense_group_settings = ExpenseGroupSettings.objects.get(
                workspace_id=workspace_id
            )
            workspace = Workspace.objects.get(pk=workspace_id)
            last_synced_at = workspace.last_synced_at if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE else None
            ccc_last_synced_at = workspace.ccc_last_synced_at if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE else None
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials)

            filter_credit_expenses = True
            if expense_group_settings.import_card_credits:
                filter_credit_expenses = False

            expenses = []
            reimbursable_expenses_count = 0

            if last_synced_at:
                last_synced_at = last_synced_at - timedelta(minutes=5)

            if FundSourceEnum.PERSONAL in fund_source:
                if imported_from == ExpenseImportSourceEnum.DIRECT_EXPORT:
                    source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL], SOURCE_ACCOUNT_MAP[FundSourceEnum.CCC]]
                else:
                    source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL]]

                expenses.extend(
                    platform.expenses.get(
                        source_account_type=source_account_type,
                        state=expense_group_settings.reimbursable_expense_state,
                        settled_at=last_synced_at
                        if expense_group_settings.reimbursable_expense_state
                        == ExpenseStateEnum.PAYMENT_PROCESSING
                        else None,
                        filter_credit_expenses=False,
                        last_paid_at=last_synced_at
                        if expense_group_settings.reimbursable_expense_state == ExpenseStateEnum.PAID
                        else None,
                    )
                )

            if workspace.last_synced_at or expenses:
                workspace.last_synced_at = datetime.now()
                reimbursable_expenses_count += len(expenses)

            if ccc_last_synced_at:
                ccc_last_synced_at = ccc_last_synced_at - timedelta(minutes=5)

            if FundSourceEnum.CCC in fund_source:
                if imported_from == ExpenseImportSourceEnum.DIRECT_EXPORT:
                    source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL], SOURCE_ACCOUNT_MAP[FundSourceEnum.CCC]]
                else:
                    source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL]]

                expenses.extend(
                    platform.expenses.get(
                        source_account_type=source_account_type,
                        state=expense_group_settings.ccc_expense_state,
                        settled_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state
                        == ExpenseStateEnum.PAYMENT_PROCESSING
                        else None,
                        approved_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state == ExpenseStateEnum.APPROVED
                        else None,
                        filter_credit_expenses=False,
                        last_paid_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state == ExpenseStateEnum.PAID
                        else None,
                    )
                )

            if workspace.ccc_last_synced_at or len(expenses) != reimbursable_expenses_count:
                workspace.ccc_last_synced_at = datetime.now()

            if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE:
                workspace.save()

            group_expenses_and_save(expenses, task_log, workspace, imported_from=imported_from, filter_credit_expenses=filter_credit_expenses)

    except FyleCredential.DoesNotExist:
        logger.info("Fyle credentials not found %s", workspace_id)
        update_task_log_post_import(
            task_log,
            TaskLogStatusEnum.FAILED,
            "Fyle credentials do not exist in workspace"
        )

    except FyleInvalidTokenError:
        logger.info("Invalid Token for Fyle")
        update_task_log_post_import(
            task_log,
            TaskLogStatusEnum.FAILED,
            "Invalid Fyle credentials"
        )

    except (RetryException, InternalServerError) as e:
        error_msg = f"Fyle {e.__class__.__name__} occurred"
        logger.info("%s in workspace_id: %s", error_msg, workspace_id)
        update_task_log_post_import(
            task_log,
            TaskLogStatusEnum.FATAL if isinstance(e, RetryException) else TaskLogStatusEnum.FAILED,
            error_msg
        )

    except Exception:
        error = traceback.format_exc()
        logger.exception(
            "Something unexpected happened workspace_id: %s",
            workspace_id
        )
        update_task_log_post_import(task_log, TaskLogStatusEnum.FATAL, error=error)


def sync_dimensions(workspace_id: int, is_export: bool = False):
    """
    Sync dimensions
    :param workspace_id: workspace id
    :param is_export: is export
    :return: None
    """
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    platform.import_fyle_dimensions(is_export=is_export)
    if is_export:
        categories_count = platform.categories.get_count()

        categories_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="CATEGORY", workspace_id=fyle_credentials.workspace_id, active=True
        ).count()

        if categories_count != categories_expense_attribute_count:
            platform.categories.sync()

        projects_count = platform.projects.get_count()

        projects_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="PROJECT", workspace_id=fyle_credentials.workspace_id, active=True
        ).count()

        if projects_count != projects_expense_attribute_count:
            platform.projects.sync()


def skip_expenses_and_post_accounting_export_summary(expense_ids: List[int], workspace: Workspace):
    """
    Skip expenses and post accounting export summary
    :param expense_ids: List of expense ids
    :param workspace: Workspace
    :return: None
    """
    skipped_expenses = mark_expenses_as_skipped(Q(), expense_ids, workspace.id)
    if skipped_expenses:
        try:
            post_accounting_export_summary(workspace_id=workspace.id, expense_ids=[expense.id for expense in skipped_expenses])
        except Exception:
            logger.exception('Error posting accounting export summary for workspace_id: %s', workspace.id)


def group_expenses_and_save(
    expenses: List[Dict],
    task_log: TaskLog,
    workspace: Workspace,
    imported_from: ExpenseImportSourceEnum = None,
    filter_credit_expenses: bool = False
):
    """
    Group expenses and save
    :param expenses: expenses
    :param task_log: task log
    :param workspace: workspace
    :param imported_from: imported from
    :param filter_credit_expenses: filter credit expenses
    """
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace.id)
    expense_objects = Expense.create_expense_objects(expenses, workspace.id, imported_from=imported_from)
    filtered_expenses = expense_objects
    expenses_object_ids = [expense_object.id for expense_object in expense_objects]

    filtered_expenses = Expense.objects.filter(
        id__in=expenses_object_ids,
        expensegroup__isnull=True,
        org_id=workspace.fyle_org_id
    )

    if filter_credit_expenses:
        negative_expense_ids = [e.id for e in expense_objects if e.amount < 0 and not e.is_skipped]
        if negative_expense_ids:
            expense_objects = [e for e in expense_objects if e.id not in negative_expense_ids]
            skip_expenses_and_post_accounting_export_summary(negative_expense_ids, workspace)

    # Skip reimbursable expenses if reimbursable expense settings is not configured
    if not configuration.reimbursable_expenses_object:
        reimbursable_expense_ids = [e.id for e in expense_objects if e.fund_source == 'PERSONAL']

        if reimbursable_expense_ids:
            expense_objects = [e for e in expense_objects if e.id not in reimbursable_expense_ids]
            skip_expenses_and_post_accounting_export_summary(reimbursable_expense_ids, workspace)

    # Skip corporate credit card expenses if corporate credit card expense settings is not configured
    if not configuration.corporate_credit_card_expenses_object:
        ccc_expense_ids = [e.id for e in expense_objects if e.fund_source == 'CCC']

        if ccc_expense_ids:
            expense_objects = [e for e in expense_objects if e.id not in ccc_expense_ids]
            skip_expenses_and_post_accounting_export_summary(ccc_expense_ids, workspace)

    filtered_expenses = expense_objects

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        filtered_expenses, workspace.id
    )

    task_log.status = 'COMPLETE'
    task_log.save()


def import_and_export_expenses(report_id: str, org_id: str, is_state_change_event: bool, report_state: str = None, imported_from: ExpenseImportSourceEnum = None) -> None:
    """
    Import and export expenses
    :param report_id: report id
    :param org_id: org id
    :return: None
    """
    workspace = Workspace.objects.get(fyle_org_id=org_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace.id)

    import_states = get_expense_import_states(expense_group_settings)

    # Don't call API if report state is not in import states, for example customer configured to import only PAID reports but webhook is triggered for APPROVED report (this is only for is_state_change_event webhook calls)
    if is_state_change_event and report_state and report_state not in import_states:
        return

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)

    try:
        with transaction.atomic():
            fund_source = get_fund_source(workspace.id)
            filter_credit_expenses = get_filter_credit_expenses(expense_group_settings)

            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

            if imported_from == ExpenseImportSourceEnum.DIRECT_EXPORT:
                source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL], SOURCE_ACCOUNT_MAP[FundSourceEnum.CCC]]
            else:
                source_account_type = get_source_account_type(fund_source)

            platform = PlatformConnector(fyle_credentials)
            expenses = platform.expenses.get(
                source_account_type,
                filter_credit_expenses=False,
                report_id=report_id,
                import_states=import_states if is_state_change_event else None
            )

            if is_state_change_event:
                expenses = filter_expenses_based_on_state(expenses, expense_group_settings)

            group_expenses_and_save(expenses, task_log, workspace, imported_from=imported_from, filter_credit_expenses=filter_credit_expenses)

        # Export only selected expense groups
        expense_ids = Expense.objects.filter(report_id=report_id, org_id=org_id).values_list('id', flat=True)
        expense_groups = ExpenseGroup.objects.filter(expenses__id__in=[expense_ids], workspace_id=workspace.id, exported_at__isnull=True).distinct('id').values('id')
        expense_group_ids = [expense_group['id'] for expense_group in expense_groups]

        if len(expense_group_ids):
            if is_state_change_event:
                # Trigger export immediately for customers who have enabled real time export
                is_real_time_export_enabled = WorkspaceSchedule.objects.filter(workspace_id=workspace.id, is_real_time_export_enabled=True).exists()

                # Don't allow real time export if it's not supported for the branded app / setting not enabled
                if not is_real_time_export_enabled or not feature_configuration.feature.real_time_export_1hr_orgs:
                    return

            logger.info(f'Exporting expenses for workspace {workspace.id} with expense group ids {expense_group_ids}, triggered by {imported_from}')
            export_to_xero(
                workspace_id=workspace.id,
                expense_group_ids=expense_group_ids,
                is_direct_export=True if not is_state_change_event else False,
                triggered_by=imported_from
            )

    except WorkspaceGeneralSettings.DoesNotExist:
        logger.info('Configuration does not exist for workspace_id: %s', workspace.id)

    except Exception:
        if not task_log:
            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

        handle_import_exception(task_log)


def update_non_exported_expenses(data: Dict) -> None:
    """
    To update expenses not in COMPLETE, IN_PROGRESS state
    """
    expense_state = None
    org_id = data['org_id']
    expense_id = data['id']
    workspace = Workspace.objects.get(fyle_org_id = org_id)
    expense = Expense.objects.filter(workspace_id=workspace.id, expense_id=expense_id).first()

    if expense:
        if 'state' in expense.accounting_export_summary:
            expense_state = expense.accounting_export_summary['state']
        else:
            expense_state = 'NOT_EXPORTED'

        if expense_state and expense_state not in ['COMPLETE', 'IN_PROGRESS']:
            expense_obj = []
            expense_obj.append(data)
            expense_objects = FyleExpenses().construct_expense_object(expense_obj, expense.workspace_id)
            Expense.create_expense_objects(
                expense_objects, expense.workspace_id, skip_update=True
            )
