from typing import List

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q

from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceSchedule
from apps.tasks.models import Error
from fyle_accounting_mappings.models import ExpenseAttribute


def get_failed_task_logs_count(workspace_id: int) -> int:
    return TaskLog.objects.filter(
        ~Q(type__in=['CREATING_BILL_PAYMENT', 'FETCHING_EXPENSES']),
        workspace_id=workspace_id,
        status='FAILED',
    ).count()


def get_admin_name(workspace_id: int, admin_email: str, ws_schedule: WorkspaceSchedule) -> str:
    attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value=admin_email).first()

    if attribute:
        return attribute.detail['full_name']
    else:
        for data in ws_schedule.additional_email_options:
            if data['email'] == admin_email:
                return data['name']


def get_errors(workspace_id: int) -> List[Error]:
    return list(Error.objects.filter(workspace_id=workspace_id, is_resolved=False).order_by('id')[:10])


def render_email_template(context: dict) -> str:
    return render_to_string("mail_template.html", context)


def send_email_notification(admin_email: str, message: str):
    mail = EmailMessage(
        subject="Export To Xero Failed",
        body=message,
        from_email=settings.EMAIL,
        to=[admin_email],
    )

    mail.content_subtype = "html"
    mail.send()