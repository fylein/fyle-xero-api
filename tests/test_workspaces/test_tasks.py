from datetime import datetime, timedelta
from apps.mappings.models import TenantMapping
from apps.tasks.models import TaskLog
from apps.workspaces.email import get_admin_name, get_errors, get_failed_task_logs_count, render_email_template, send_email_notification
from apps.workspaces.tasks import run_email_notification, run_sync_schedule, schedule_sync, async_update_fyle_credentials
from apps.workspaces.models import WorkspaceSchedule, WorkspaceGeneralSettings, LastExportDetail, \
    FyleCredential
    
from .fixtures import data

import pytest

def test_schedule_sync(db):
    workspace_id = 1
    
    schedule_sync(workspace_id, True, 1, {}, [])

    ws_schedule = WorkspaceSchedule.objects.filter( 
        workspace_id=workspace_id 
    ).first() 
    
    assert ws_schedule.schedule.func == 'apps.workspaces.tasks.run_sync_schedule'

    schedule_sync(workspace_id, False, 1, {}, [])

    ws_schedule = WorkspaceSchedule.objects.filter( 
        workspace_id=workspace_id 
    ).first() 

    assert ws_schedule.schedule == None


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

    ws_schedule, _ = WorkspaceSchedule.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'enabled': True
        }
    )
    ws_schedule.enabled = True
    ws_schedule.emails_selected = ['anishkumar.s@fyle.in']
    ws_schedule.save()

    run_email_notification(1)

    workspace_id = 1
    ws_schedule, _ = WorkspaceSchedule.objects.update_or_create(
        workspace_id=workspace_id 
    ) 
    ws_schedule.enabled = True
    ws_schedule.emails_selected = ['anishkumar.s@fyle.in']
    ws_schedule.additional_email_options = [{'email': 'anishkumar.s@fyle.in', 'name': 'Anish'}]
    ws_schedule.save()

    run_email_notification(1)


def test_run_email_notification1(db):
    workspace_id = 1
    ws_schedule, _ = WorkspaceSchedule.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'enabled': True
        }
    )

    # Assert that ws_schedule is enabled after it is updated or created
    assert ws_schedule.enabled == True

    task_logs_count = 10
    ws_schedule.error_count = None
    run_email_notification(workspace_id)
    ws_schedule.emails_selected = ["admin1@example.com", "admin2@example.com"]
    test_tenant_detail, _ = TenantMapping.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'tenant_name': 'Test Tenant'
        }
    )

    # Assert that ws_schedule.emails_selected is equal to ["admin1@example.com", "admin2@example.com"]
    assert ws_schedule.emails_selected == ["admin1@example.com", "admin2@example.com"]

    test_error1 = {"type": "ERROR_TYPE_1"}
    test_error2 = {"type": "ERROR_TYPE_2"}
    errors = [test_error1, test_error2]

    # Call functions to get count of failed task logs, errors, and admin name
    get_failed_task_logs_count(workspace_id)
    get_errors(workspace_id)
    get_admin_name(workspace_id, "admin1@example.com", ws_schedule)

    # Call TenantMapping.get_tenant_details to get tenant details
    TenantMapping.get_tenant_details(workspace_id)
    context = {
        'name': "Test Admin",
        'errors_count': task_logs_count,
        'fyle_company': 'Fyle for Arkham Asylum',
        'xero_tenant': test_tenant_detail.tenant_name,
        'export_time': '2023-03-15 11:29:33.110744+00',
        'year': '2022',
        'app_url': "https://example.com/workspaces/main/dashboard",
        'errors': errors,
        'error_type': 'Error Type 1, Error Type 2'
    }

    # Assert that render_email_template returns a string
    assert isinstance(render_email_template(context), str)

    # Test with task_logs_count == 0
    task_logs_count = 0
    ws_schedule.error_count = None
    run_email_notification(workspace_id)
    ws_schedule.emails_selected = ["admin1@example.com"]
    get_failed_task_logs_count(workspace_id)
    TenantMapping.get_tenant_details(workspace_id)
    ws_schedule.save()

    # Test with ws_schedule.error_count >= task_logs_count
    task_logs_count = 5
    ws_schedule.error_count = 10
    run_email_notification(workspace_id)
    ws_schedule.emails_selected = []
    get_failed_task_logs_count(workspace_id)
    get_errors(workspace_id)
    TenantMapping.get_tenant_details(workspace_id)
    ws_schedule.save()

    # Test with no emails selected
    task_logs_count = 10
    ws_schedule.error_count = None
    run_email_notification(workspace_id)
    ws_schedule.emails_selected = []
    get_failed_task_logs_count(workspace_id)
    get_errors(workspace_id)
    TenantMapping.get_tenant_details(workspace_id)
    ws_schedule.save()


def test_run_email_notification_with_invalid_workspace_id(db):
    workspace_id = None
    with pytest.raises(Exception):
        run_email_notification(workspace_id)
