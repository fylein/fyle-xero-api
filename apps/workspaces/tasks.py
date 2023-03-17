from datetime import date, datetime, timedelta
from typing import List
import logging

from django_q.models import Schedule

from django.template import loader
from django.core.mail import EmailMessage
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q

from apps.fyle.models import ExpenseGroup
from apps.fyle.tasks import async_create_expense_groups
from apps.mappings.models import TenantMapping
from apps.workspaces.email import get_admin_name, get_errors, get_failed_task_logs_count, render_email_template, send_email_notification
from apps.xero.tasks import schedule_bills_creation, schedule_bank_transaction_creation, create_chain_and_export
from apps.tasks.models import TaskLog
from apps.workspaces.models import Workspace, WorkspaceSchedule, WorkspaceGeneralSettings, LastExportDetail, FyleCredential, XeroCredentials
from apps.tasks.models import Error
from fyle_accounting_mappings.models import ExpenseAttribute

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def schedule_email_notification(workspace_id: int, schedule_enabled: bool, hours: int):
    if schedule_enabled:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.workspaces.tasks.run_email_notification',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': hours * 60,
                'next_run': datetime.now() + timedelta(minutes=10)
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.workspaces.tasks.run_email_notification',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_sync(workspace_id: int, schedule_enabled: bool, hours: int, email_added: List, emails_selected: List):
    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )

    schedule_email_notification(workspace_id=workspace_id, schedule_enabled=schedule_enabled, hours=hours)

    if schedule_enabled:
        ws_schedule.enabled = schedule_enabled
        ws_schedule.start_datetime = datetime.now()
        ws_schedule.interval_hours = hours
        ws_schedule.emails_selected = emails_selected

        if email_added:
            ws_schedule.additional_email_options.append(email_added)

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
    fyle_credentials = FyleCredential.objects.filter(workspace__fyle_org_id=fyle_org_id).first()
    if fyle_credentials:
        fyle_credentials.refresh_token = refresh_token
        fyle_credentials.save()


def run_email_notification(workspace_id):
    ws_schedule = WorkspaceSchedule.objects.get(
        workspace_id=workspace_id, enabled=True
    )

    task_logs_count = get_failed_task_logs_count(workspace_id)
    workspace = Workspace.objects.get(id=workspace_id)
    tenant_detail = TenantMapping.get_tenant_details(workspace_id)
    # task_logs_count and (ws_schedule.error_count is None or task_logs_count > ws_schedule.error_count):
    if True:
        errors = get_errors(workspace_id)
        for admin_email in ws_schedule.emails_selected:
            admin_name = get_admin_name(workspace_id, admin_email, ws_schedule)
            error_types = {error.type.title().replace('_', ' ') for error in errors}
            context = {
                'name': admin_name,
                'errors_count': task_logs_count,
                'fyle_company': workspace.name,
                'xero_tenant': tenant_detail.tenant_name,
                'export_time': workspace.last_synced_at.strftime("%d %b %Y | %H:%M"),
                'year': date.today().year,
                'app_url': "{0}/workspaces/main/dashboard".format(settings.FYLE_APP_URL),
                'errors': errors,
                'error_type': ', '.join(error_types)
            }
            message = render_email_template(context)
            send_email_notification(admin_email, message)

        ws_schedule.error_count = task_logs_count
        ws_schedule.save()