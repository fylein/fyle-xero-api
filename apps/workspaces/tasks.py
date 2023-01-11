from datetime import datetime

from django_q.models import Schedule

from apps.fyle.models import ExpenseGroup
from apps.fyle.tasks import async_create_expense_groups
from apps.xero.tasks import schedule_bills_creation, schedule_bank_transaction_creation, create_chain_and_export
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceSchedule, WorkspaceGeneralSettings, LastExportDetail, FyleCredential


def schedule_sync(workspace_id: int, schedule_enabled: bool, hours: int):
    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )

    if schedule_enabled:
        ws_schedule.enabled = schedule_enabled
        ws_schedule.start_datetime = datetime.now()
        ws_schedule.interval_hours = hours

        schedule, _ = Schedule.objects.update_or_create(
            func='apps.workspaces.tasks.run_sync_schedule',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': hours * 60,
                'next_run': datetime.now()
            }
        )

        ws_schedule.schedule = schedule

        ws_schedule.save()

    elif not schedule_enabled and ws_schedule.schedule:
        schedule = ws_schedule.schedule
        ws_schedule.enabled = schedule_enabled
        ws_schedule.schedule = None
        ws_schedule.save()
        schedule.delete()

    return ws_schedule


def run_sync_schedule(workspace_id):
    """
    Run schedule
    :param user: user email
    :param workspace_id: workspace id
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

    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if general_settings.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    async_create_expense_groups(
        workspace_id=workspace_id, fund_source=fund_source, task_log=task_log
    )

    if task_log.status == 'COMPLETE':
        export_to_xero(workspace_id, 'AUTO')

def export_to_xero(workspace_id, export_mode='MANUAL'):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    last_exported_at = datetime.now()
    chaining_attributes = []

    if general_settings.reimbursable_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(fund_source='PERSONAL').values_list('id', flat=True)
        chaining_attributes.extend(schedule_bills_creation(workspace_id, expense_group_ids))

    if general_settings.corporate_credit_card_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(fund_source='CCC').values_list('id', flat=True)
        chaining_attributes.extend(schedule_bank_transaction_creation(workspace_id, expense_group_ids))

    if chaining_attributes:
        create_chain_and_export(chaining_attributes, workspace_id)
        last_export_detail.last_exported_at = last_exported_at
        last_export_detail.export_mode = export_mode
        last_export_detail.save()

def async_update_fyle_credentials(fyle_org_id: str, refresh_token: str):
    fyle_credentials = FyleCredential.objects.get(workspace__fyle_org_id=fyle_org_id)
    if fyle_credentials:
        fyle_credentials.refresh_token = refresh_token
        fyle_credentials.save()
