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
    """
    Returns the count of failed TaskLog objects that match certain criteria.
    
    Args:
        workspace_id (int): The ID of the workspace.
    
    Returns:
        int: The count of failed TaskLog objects.
    """
    return TaskLog.objects.filter(
        ~Q(type__in=['CREATING_BILL_PAYMENT', 'FETCHING_EXPENSES']),
        workspace_id=workspace_id,
        status='FAILED',
    ).count()


def get_admin_name(workspace_id: int, admin_email: str, ws_schedule: WorkspaceSchedule) -> str:
    """
    Returns the name of the admin associated with the given email address.
    
    Args:
        workspace_id (int): The ID of the workspace.
        admin_email (str): The email address of the admin.
        ws_schedule (WorkspaceSchedule): The workspace schedule.
    
    Returns:
        str: The full name of the admin.
    """
    attribute = ExpenseAttribute.objects.filter(workspace_id=workspace_id, value=admin_email).first()

    if attribute:
        return attribute.detail['full_name']
    else:
        for data in ws_schedule.additional_email_options:
            if data['email'] == admin_email:
                return data['name']


def get_errors(workspace_id: int) -> List[Error]:
    """
    Returns a list of Error objects that match certain criteria.
    
    Args:
        workspace_id (int): The ID of the workspace.
    
    Returns:
        List[Error]: A list of Error objects.
    """
    return list(Error.objects.filter(workspace_id=workspace_id, is_resolved=False).order_by('id')[:10])


def render_email_template(context: dict) -> str:
    """
    Renders an email template with the provided context.
    
    Args:
        context (dict): The context to use when rendering the template.
    
    Returns:
        str: The rendered template as a string.
    """
    return render_to_string("mail_template.html", context)


def send_email_notification(admin_email: str, message: str):
    """
    Sends an email notification to a specified admin email address.
    
    Args:
        admin_email (str): The email address of the admin.
        message (str): The message to include in the email.
    """
    mail = EmailMessage(
        subject="Export To Xero Failed",
        body=message,
        from_email=settings.EMAIL,
        to=[admin_email],
    )

    mail.content_subtype = "html"
    mail.send()
