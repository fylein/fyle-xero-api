from apps.tasks.models import TaskLog
from apps.workspaces.tasks import run_sync_schedule, schedule_sync
from apps.workspaces.models import WorkspaceSchedule, WorkspaceGeneralSettings
from .fixtures import data


def test_schedule_sync(db):
    workspace_id = 1
    
    schedule_sync(workspace_id, True, 1)

    ws_schedule = WorkspaceSchedule.objects.filter( 
        workspace_id=workspace_id 
    ).first() 
    
    assert ws_schedule.schedule.func == 'apps.workspaces.tasks.run_sync_schedule'

    schedule_sync(workspace_id, False, 1)

    ws_schedule = WorkspaceSchedule.objects.filter( 
        workspace_id=workspace_id 
    ).first() 

    assert ws_schedule.schedule == None

# Fix this while we are in the dashboard module.
# def test_run_sync_schedule(mocker,db):
#     workspace_id = 1

#     general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
#     mocker.patch(
#         'fyle_integrations_platform_connector.apis.Expenses.get',
#         return_value=data['expenses']
#     )

#     run_sync_schedule(workspace_id)

#     task_log = TaskLog.objects.filter(
#         workspace_id=workspace_id
#     ).first()
    
#     assert task_log.status == 'COMPLETE'

#     general_settings.reimbursable_expenses_object = 'PURCHASE BILL'
#     general_settings.corporate_credit_card_expenses_object = 'BANK TRANSACTION'
#     general_settings.save()

#     run_sync_schedule(workspace_id)
    
#     task_log = TaskLog.objects.filter(
#         workspace_id=workspace_id
#     ).first()
    
#     assert task_log.status == 'COMPLETE'
