from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.workspaces.models import FyleCredential
from apps.fyle.tasks import schedule_expense_group_creation, create_expense_groups
from apps.tasks.models import TaskLog
from .fixtures import data
from unittest import mock

from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError


def test_schedule_expense_group_creation(api_client, test_connection):
    workspace_id = 1

    expense_groups = ExpenseGroup.objects.filter(workspace_id=workspace_id).count()
    assert expense_groups == 10
    
    schedule_expense_group_creation(workspace_id=workspace_id)

    expense_groups = ExpenseGroup.objects.filter(workspace_id=workspace_id).count()
    assert expense_groups == 10


def test_create_expense_groups(mocker, db):
    workspace_id = 1
    
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=data['expenses']
    )

    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.reimbursable_export_date_type = 'last_spent_at'
    expense_group_settings.ccc_export_date_type = 'last_spent_at'
    expense_group_settings.save()

    create_expense_groups(workspace_id, ['PERSONAL', 'CCC'], task_log)

    task_log = TaskLog.objects.get(id=task_log.id)

    assert task_log.status == 'COMPLETE'

    fyle_credential = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credential.delete()

    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'IN_PROGRESS'
        }
    )
    create_expense_groups(workspace_id, ['PERSONAL', 'CCC'], task_log)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status == 'FAILED'

    with mock.patch('yle.platform.apis.v1beta.admin.Expenses.list_all') as mock_call:
        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for Fyle', response="Invalid Token for Fyle")
        create_expense_groups(workspace_id, ['PERSONAL', 'CCC'], task_log)

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.delete()

    create_expense_groups(workspace_id, ['PERSONAL', 'CCC'], task_log)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status == 'FATAL' 
