import logging
from typing import List
import traceback
from datetime import datetime

from django.db import transaction
from django_q.tasks import async_task

from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings
from apps.tasks.models import TaskLog

from fyle_integrations_platform_connector import PlatformConnector

from .models import Expense, ExpenseGroup, ExpenseGroupSettings


logger = logging.getLogger(__name__)
logger.level = logging.INFO

SOURCE_ACCOUNT_MAP = {
    'PERSONAL': 'PERSONAL_CASH_ACCOUNT',
    'CCC': 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
}

def get_task_log_and_fund_source(workspace_id: int):
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if general_settings.corporate_credit_card_expenses_object is not None:
        fund_source.append('CCC')

    return task_log, fund_source


def schedule_expense_group_creation(workspace_id: int):
    """
    Schedule Expense group creation
    :param workspace_id: Workspace id
    :return: None
    """
    task_log, fund_source = get_task_log_and_fund_source(workspace_id)

    async_task('apps.fyle.tasks.create_expense_groups', workspace_id, fund_source, task_log)


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

    task_log.detail = {
        'message': 'Creating expense groups'
    }
    task_log.save()

    return task_log


def async_create_expense_groups(workspace_id: int, fund_source: List[str], task_log: TaskLog):
    try:
        with transaction.atomic():

            expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
            workspace = Workspace.objects.get(pk=workspace_id)
            last_synced_at = workspace.last_synced_at
            ccc_last_synced_at = workspace.ccc_last_synced_at
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials)

            filter_credit_expenses = True
            if expense_group_settings.import_card_credits:
                filter_credit_expenses = False

            expenses, source_account_type = [], []
            reimbursable_expenses_count = 0

            for source in fund_source:
                source_account_type.append(SOURCE_ACCOUNT_MAP[source])

            if 'PERSONAL' in fund_source:
                expenses.extend(platform.expenses.get(
                    source_account_type=['PERSONAL_CASH_ACCOUNT'],
                    state=expense_group_settings.reimbursable_expense_state,
                    settled_at=last_synced_at if expense_group_settings.reimbursable_expense_state == 'PAYMENT_PROCESSING' else None,
                    filter_credit_expenses=filter_credit_expenses,
                    last_paid_at=last_synced_at if expense_group_settings.reimbursable_expense_state == 'PAID' else None
                ))

            if expenses:
                workspace.last_synced_at = datetime.now()
                reimbursable_expenses_count += len(expenses)

            if 'CCC' in fund_source:
                expenses.extend(platform.expenses.get(
                    source_account_type=['PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'],
                    state=expense_group_settings.ccc_expense_state,
                    settled_at=ccc_last_synced_at if expense_group_settings.ccc_expense_state == 'PAYMENT_PROCESSING' else None,
                    approved_at=ccc_last_synced_at if expense_group_settings.ccc_expense_state == 'APPROVED' else None,
                    filter_credit_expenses=filter_credit_expenses,
                    last_paid_at=ccc_last_synced_at if expense_group_settings.ccc_expense_state == 'PAID' else None
                ))

            if len(expenses) != reimbursable_expenses_count:
                workspace.ccc_last_synced_at = datetime.now()

            workspace.save()

            expense_objects = Expense.create_expense_objects(expenses, workspace_id)

            ExpenseGroup.create_expense_groups_by_report_id_fund_source(
                expense_objects, workspace_id
            )

            task_log.status = 'COMPLETE'

            task_log.save()

    except FyleCredential.DoesNotExist:
        logger.info('Fyle credentials not found %s', workspace_id)
        task_log.detail = {
            'message': 'Fyle credentials do not exist in workspace'
        }
        task_log.status = 'FAILED'
        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)
