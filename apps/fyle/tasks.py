import logging
from typing import List
import traceback
from datetime import datetime

from django.db import transaction
from django_q.tasks import async_task

from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings
from apps.tasks.models import TaskLog

from .models import Expense, ExpenseGroup, ExpenseGroupSettings
from .utils import FyleConnector
from .platform_connector import PlatformConnector
from .serializers import ExpenseGroupSerializer
from .helpers import compare_tpa_and_platform_expenses

logger = logging.getLogger(__name__)
logger.level = logging.INFO

def schedule_expense_group_creation(workspace_id: int):
    """
    Schedule Expense group creation
    :param workspace_id: Workspace id
    :return: None
    """
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = ['PERSONAL']
    if general_settings.corporate_credit_card_expenses_object is not None:
        fund_source.append('CCC')

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

            workspace = Workspace.objects.get(pk=workspace_id)

            last_synced_at = workspace.last_synced_at

            # Remove this later
            updated_at_fyle_tpa = []

            updated_at = None

            if last_synced_at:
                updated_at = 'gte.{}'.format(datetime.strftime(last_synced_at, '%Y-%m-%dT%H:%M:%S.000Z'))

                # Remove this later
                updated_at_fyle_tpa.append(
                    'gte:{0}'.format(datetime.strftime(last_synced_at, '%Y-%m-%dT%H:%M:%S.000Z'))
                )

            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

            # Remove this later
            fyle_connector = FyleConnector(fyle_credentials.refresh_token, workspace_id)

            platform_connector = PlatformConnector(fyle_credentials.refresh_token, workspace_id)

            expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)

            source_account_type = ['PERSONAL_CASH_ACCOUNT']
            if len(fund_source) == 1:
                source_account_type = 'eq.{}'.format(source_account_type[0])
            elif len(fund_source) > 1 and 'CCC' in fund_source:
                source_account_type.append('PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT')
                source_account_type = 'in.{}'.format(tuple(source_account_type)).replace("'", '"')

            # Remove this later
            tpa_expenses = fyle_connector.get_expenses(
                state=expense_group_settings.expense_state,
                updated_at=updated_at_fyle_tpa,
                fund_source=fund_source
            )

            expenses = platform_connector.get_expenses(
                state=expense_group_settings.expense_state,
                updated_at=updated_at,
                fund_source=source_account_type
            )

            compare_tpa_and_platform_expenses(tpa_expenses, expenses, workspace_id)

            if expenses:
                workspace.last_synced_at = datetime.now()
                workspace.save()

            expense_objects = Expense.create_expense_objects(expenses, workspace_id)

            expense_group_objects = ExpenseGroup.create_expense_groups_by_report_id_fund_source(
                expense_objects, workspace_id
            )

            task_log.detail = ExpenseGroupSerializer(expense_group_objects, many=True).data

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
