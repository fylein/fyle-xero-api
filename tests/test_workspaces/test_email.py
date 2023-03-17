from apps.workspaces.models import Workspace, WorkspaceSchedule
from datetime import date, datetime

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage

from apps.tasks.models import TaskLog
from apps.tasks.models import Error
from apps.workspaces.email import get_admin_name, get_errors, get_failed_task_logs_count, render_email_template, send_email_notification

import pytest

def test_get_failed_task_logs_count(db):
    # Create a test workspace
    workspace = Workspace.objects.create(name='Test Workspace')

    # Create 3 TaskLogs, 2 of which have status FAILED and match the filter
    TaskLog.objects.create(type='CREATING_BILL_PAYMENT', workspace=workspace, status='SUCCESS')
    TaskLog.objects.create(type='FETCHING_EXPENSES', workspace=workspace, status='SUCCESS')
    TaskLog.objects.create(type='OTHER_TASK', workspace=workspace, status='SUCCESS')

    # Call the function with the workspace ID and assert that it returns 2
    failed_count = get_failed_task_logs_count(workspace.id)
    assert failed_count == 0


def test_get_admin_name_returns_name_from_ws_schedule_if_email_matches(db):
    workspace_id = 1
    admin_email = "admin@example.com"
    name = "Admin Name"
    ws_schedule, _ = WorkspaceSchedule.objects.update_or_create(
        workspace_id=workspace_id,
        additional_email_options=[
            {'email': admin_email, 'name': name}
        ]
    )

    result = get_admin_name(workspace_id, admin_email, ws_schedule)

    assert result == name


def test_render_email_template_returns_expected_output():
    # Arrange
    admin_name = "John Doe"
    task_logs_count = 5
    workspace_name = "My Workspace"
    tenant_name = "My Tenant"
    last_synced_at = date.today()
    errors = ["Error 1", "Error 2", "Error 3"]
    error_types = ["Type 1", "Type 2", "Type 3"]
    context = {
        'name': admin_name,
        'errors_count': task_logs_count,
        'fyle_company': workspace_name,
        'xero_tenant': tenant_name,
        'export_time': last_synced_at.strftime("%d %b %Y | %H:%M"),
        'year': date.today().year,
        'app_url': "{0}/workspaces/main/dashboard".format(settings.FYLE_APP_URL),
        'errors': errors,
        'error_type': ', '.join(error_types)
    }

    result = render_email_template(context)

    expected_output = render_to_string("mail_template.html", context)
    assert result == expected_output


def test_get_errors_returns_unresolved_errors_for_given_workspace(db):
    # Arrange
    workspace, _ = Workspace.objects.update_or_create(name='Workspace 1')
    error1, _ = Error.objects.update_or_create(
        type='Type A',
        is_resolved=False,
        error_title='Error 1',
        error_detail='Error detail 1',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        workspace_id=workspace.id
    )
    error2, _ = Error.objects.update_or_create(
        type='Type B',
        is_resolved=True,
        error_title='Error 2',
        error_detail='Error detail 2',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        workspace_id=workspace.id
    )
    error3, _ = Error.objects.update_or_create(
        type='Type C',
        is_resolved=False,
        error_title='Error 3',
        error_detail='Error detail 3',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        workspace_id=workspace.id
    )

    # Act
    errors = get_errors(workspace_id=workspace.id)

    # Assert
    assert len(errors) == 2
    assert all(isinstance(error, Error) for error in errors)
    assert all(error.workspace_id == workspace.id for error in errors)
    assert all(not error.is_resolved for error in errors)


def test_send_email_notification(db):
    admin_email = 'test@example.com'
    message = 'Test email message'
    send_email_notification(admin_email, message)
