from datetime import date
from typing import List

from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from fyle_accounting_mappings.models import ExpenseAttribute
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import From, Mail

from apps.mappings.models import TenantMapping
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import Workspace, WorkspaceSchedule


def get_failed_task_logs_count(workspace_id: int) -> int:
    """
    Returns the count of failed TaskLog objects that match certain criteria.

    Args:
        workspace_id (int): The ID of the workspace.

    Returns:
        int: The count of failed TaskLog objects.
    """
    return TaskLog.objects.filter(
        ~Q(type__in=[TaskLogTypeEnum.CREATING_PAYMENT, TaskLogTypeEnum.FETCHING_EXPENSES]),
        workspace_id=workspace_id,
        status=TaskLogStatusEnum.FAILED,
    ).count()


def get_admin_name(
    workspace_id: int, admin_email: str, ws_schedule: WorkspaceSchedule
) -> str:
    """
    Returns the name of the admin associated with the given email address.

    Args:
        workspace_id (int): The ID of the workspace.
        admin_email (str): The email address of the admin.
        ws_schedule (WorkspaceSchedule): The workspace schedule.

    Returns:
        str: The full name of the admin.
    """
    attribute = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id, value=admin_email
    ).first()

    if attribute:
        return attribute.detail["full_name"]
    else:
        for data in ws_schedule.additional_email_options:
            if data["email"] == admin_email:
                return data["name"]


def get_errors(workspace_id: int) -> List[Error]:
    """
    Returns a list of Error objects that match certain criteria.

    Args:
        workspace_id (int): The ID of the workspace.

    Returns:
        List[Error]: A list of Error objects.
    """
    return list(
        Error.objects.filter(workspace_id=workspace_id, is_resolved=False).order_by(
            "id"
        )[:10]
    )


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
    SENDGRID_API_KEY = settings.SENDGRID_API_KEY
    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = From(email=settings.EMAIL)
    mail = Mail(
        from_email=from_email,
        to_emails=[admin_email],
        subject="Export To Xero Failed",
        html_content=message
    )
    sg.send(mail)


def send_failure_notification_email(
    admin_name: str,
    admin_email: str,
    task_logs_count: int,
    workspace: Workspace,
    tenant_detail: TenantMapping,
    errors: List[Error],
):
    error_types = {error.type.title().replace("_", " ") for error in errors}
    context = {
        "name": admin_name,
        "errors_count": task_logs_count,
        "fyle_company": workspace.name,
        "xero_tenant": tenant_detail.tenant_name,
        "export_time": workspace.last_synced_at.strftime("%d %b %Y | %H:%M"),
        "year": date.today().year,
        "app_url": "{0}/app/admin/#/integrations?integrationIframeTarget=integrations/xero".format(settings.FYLE_APP_URL),
        "errors": errors,
        "error_type": ", ".join(error_types),
        "integrations_app_url": settings.INTEGRATIONS_APP_URL
    }
    message = render_email_template(context)
    send_email_notification(admin_email, message)
