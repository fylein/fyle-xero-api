from datetime import datetime, timedelta
from apps.mappings.models import TenantMapping
from apps.tasks.models import TaskLog
from apps.workspaces.email import get_admin_name, get_errors, get_failed_task_logs_count, render_email_template
from apps.workspaces.tasks import run_email_notification, run_sync_schedule, schedule_sync, async_update_fyle_credentials
from apps.workspaces.models import WorkspaceSchedule, WorkspaceGeneralSettings, LastExportDetail, \
    FyleCredential

from fyle_accounting_mappings.models import ExpenseAttribute

from .fixtures import data

import pytest

def test_schedule_sync(db):
    workspace_id = 1

    # Test with email_added
    email_added = {'email': 'test@example.com', 'name': 'Test User'}
    schedule_sync(workspace_id, True, 1, email_added, [])

    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()

    assert ws_schedule.schedule.func == 'apps.workspaces.tasks.run_sync_schedule'
    assert ws_schedule.additional_email_options == [email_added]

    # Test without email_added
    schedule_sync(workspace_id, False, 1, {}, [])

    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()

    assert ws_schedule.schedule is None


def test_run_sync_schedule(mocker,db):
    workspace_id = 1

    LastExportDetail.objects.create(
        last_exported_at=datetime.now(),
        export_mode='MANUAL',
        workspace_id=1
    )
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=data['expenses']
    )

    run_sync_schedule(workspace_id)

    task_log = TaskLog.objects.filter(
        workspace_id=workspace_id
    ).first()
    
    assert task_log.status == 'COMPLETE'

    general_settings.reimbursable_expenses_object = 'PURCHASE BILL'
    general_settings.corporate_credit_card_expenses_object = 'BANK TRANSACTION'
    general_settings.save()

    run_sync_schedule(workspace_id)
    
    task_log = TaskLog.objects.filter(
        workspace_id=workspace_id
    ).first()
    
    assert task_log.status == 'COMPLETE'


def test_async_update_fyle_credentials(db):
    workspace_id = 1
    refresh_token = 'hehehuhu'

    async_update_fyle_credentials('orPJvXuoLqvJ', refresh_token)

    fyle_credentials = FyleCredential.objects.filter(workspace_id=workspace_id).first()

    assert fyle_credentials.refresh_token == refresh_token


def test_email_notification(db):
    workspace_id = 1

    # Create failed task logs
    TaskLog.objects.create(workspace_id=workspace_id, status='FAILED', type='IMPORTING_EXPENSES')
    TaskLog.objects.create(workspace_id=workspace_id, status='FAILED', type='CREATING_BILL_PAYMENT')
    TaskLog.objects.create(workspace_id=workspace_id, status='COMPLETED', type='FETCHING_EXPENSES')

    ws_schedule, _ = WorkspaceSchedule.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'enabled': True,
            'error_count': None
        }
    )
    ws_schedule.enabled = True
    ws_schedule.emails_selected = ['anishkumar.s@fyle.in']
    ws_schedule.save()

    # Check that email is not sent when error count is None and there are no failed task logs
    run_email_notification(workspace_id)

    # Check that email is sent when there are failed task logs and error count is None
    ws_schedule.error_count = None
    ws_schedule.save()
    run_email_notification(workspace_id)
    

    # Check that email is sent when there are failed task logs and error count is less than task_logs_count
    ws_schedule.error_count = 1
    ws_schedule.save()
    run_email_notification(workspace_id)
    

    # Check that email is not sent when there are failed task logs but error count is greater than task_logs_count
    ws_schedule.error_count = 3
    ws_schedule.save()
    run_email_notification(workspace_id)
    

    # Check that email is sent to admin name from ExpenseAttribute
    ExpenseAttribute.objects.create(workspace_id=workspace_id, value='anishkumar.s@fyle.in', detail={'full_name': 'Anish Kumar'})

    ws_schedule.emails_selected = ['anishkumar.s@fyle.in']
    ws_schedule.additional_email_options = []
    ws_schedule.save()
    run_email_notification(workspace_id)

    # Check that email is sent to name from additional_email_options
    ws_schedule.additional_email_options = [{'email': 'anishkumar.s@fyle.in', 'name': 'Anish'}]
    ws_schedule.save()
    run_email_notification(workspace_id)


def test_run_email_notification_with_invalid_workspace_id(db):
    workspace_id = None
    with pytest.raises(Exception):
        run_email_notification(workspace_id)
