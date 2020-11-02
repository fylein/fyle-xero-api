import logging
from typing import List
import traceback
from datetime import datetime

from django.conf import settings
from django.db import transaction
from django_q.tasks import async_task

from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings
from apps.tasks.models import TaskLog

from .models import Expense, ExpenseGroup, ExpenseGroupSettings
from .utils import FyleConnector
from .serializers import ExpenseGroupSerializer

logger = logging.getLogger(__name__)


def schedule_expense_group_creation(workspace_id: int):
    """
    Schedule Expense group creation
    :param workspace_id: Workspace id
    :param user: User email
    :return: None
    """
    task_log = TaskLog.objects.create(
        workspace_id=workspace_id,
        type='FETCHING_EXPENSES',
        status='IN_PROGRESS'
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = ['PERSONAL']
    if general_settings.corporate_credit_card_expenses_object is not None:
        fund_source.append('CCC')

    async_task('apps.fyle.tasks.create_expense_groups', workspace_id, fund_source, task_log)

    task_log.save()


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
    task_log.save(update_fields=['task_id', 'detail'])

    return task_log


def async_create_expense_groups(workspace_id: int, fund_source: List[str], task_log: TaskLog):
    try:
        with transaction.atomic():

            workspace = Workspace.objects.get(pk=workspace_id)

            last_synced_at = workspace.last_synced_at

            updated_at = []

            if last_synced_at:
                updated_at.append('gte:{0}'.format(datetime.strftime(last_synced_at, '%Y-%m-%dT%H:%M:%S.000Z')))

            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

            fyle_connector = FyleConnector(fyle_credentials.refresh_token, workspace_id)

            expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)

            expenses = fyle_connector.get_expenses(
                state=expense_group_settings.expense_state,
                updated_at=updated_at,
                fund_source=fund_source
            )

            if expenses:
                workspace.last_synced_at = datetime.now()
                workspace.save()

            custom_fields = fyle_connector.sync_expense_custom_fields(active_only=True)

            expense_objects = Expense.create_expense_objects(expenses, custom_fields)

            expense_group_objects = ExpenseGroup.create_expense_groups_by_report_id_fund_source(
                expense_objects, workspace_id
            )

            task_log.detail = ExpenseGroupSerializer(expense_group_objects, many=True).data

            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'status'])

    except FyleCredential.DoesNotExist:
        logger.exception('Fyle credentials not found %s', workspace_id)
        task_log.detail = {
            'message': 'Fyle credentials do not exist in workspace'
        }
        task_log.status = 'FAILED'
        task_log.save(update_fields=['detail', 'status'])

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save(update_fields=['detail', 'status'])
        logger.exception('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)
