from datetime import datetime
from apps.tasks.models import TaskLog
from apps.workspaces.tasks import run_sync_schedule, schedule_sync, async_update_fyle_credentials
from apps.workspaces.models import WorkspaceSchedule, WorkspaceGeneralSettings, LastExportDetail, \
    FyleCredential

from .fixtures import data


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