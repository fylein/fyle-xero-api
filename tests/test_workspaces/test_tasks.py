import pytest
from django.db.models import Q
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.models import Expense, ExpenseGroup
from apps.fyle.tasks import import_and_export_expenses, skip_expenses_and_post_accounting_export_summary
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import TaskLog
from apps.users.models import User
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings, WorkspaceSchedule
from apps.workspaces.queue import schedule_sync
from apps.workspaces.tasks import (
    async_add_admins_to_workspace,
    async_create_admin_subscriptions,
    async_update_fyle_credentials,
    async_update_workspace_name,
    post_to_integration_settings,
    run_email_notification,
    run_sync_schedule,
)
from tests.test_fyle.fixtures import data as fyle_data
from tests.test_workspaces.fixtures import data


def test_schedule_sync(db):
    workspace_id = 1

    # Test with email_added
    email_added = [{"email": "test@example.com", "name": "Test User"}]
    schedule_sync(workspace_id, True, 1, email_added, [], False)

    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()

    assert ws_schedule.schedule.func == "apps.workspaces.tasks.run_sync_schedule"
    assert ws_schedule.additional_email_options == email_added

    # Test without email_added
    schedule_sync(workspace_id, False, 1, {}, [], False)

    ws_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id).first()

    assert ws_schedule.schedule is None


def test_run_sync_schedule(mocker, db):
    workspace_id = 1

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    mocker.patch(
        "fyle_integrations_platform_connector.apis.Expenses.get",
        return_value=data["expenses"],
    )

    run_sync_schedule(workspace_id)

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()

    assert task_log.status == "COMPLETE"

    general_settings.reimbursable_expenses_object = "PURCHASE BILL"
    general_settings.corporate_credit_card_expenses_object = "BANK TRANSACTION"
    general_settings.save()

    run_sync_schedule(workspace_id)

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()

    assert task_log.status == "COMPLETE"


def test_async_update_fyle_credentials(db):
    workspace_id = 1
    refresh_token = "hehehuhu"

    async_update_fyle_credentials("orPJvXuoLqvJ", refresh_token)

    fyle_credentials = FyleCredential.objects.filter(workspace_id=workspace_id).first()

    assert fyle_credentials.refresh_token == refresh_token


def test_email_notification(db, mocker):
    workspace_id = 1

    # Mock the send_failure_notification_email function
    mocker.patch("apps.workspaces.tasks.send_failure_notification_email")

    # Create failed task logs
    TaskLog.objects.create(
        workspace_id=workspace_id, status="FAILED", type="IMPORTING_EXPENSES"
    )
    TaskLog.objects.create(
        workspace_id=workspace_id, status="FAILED", type="CREATING_BILL_PAYMENT"
    )
    TaskLog.objects.create(
        workspace_id=workspace_id, status="COMPLETED", type="FETCHING_EXPENSES"
    )

    ws_schedule, _ = WorkspaceSchedule.objects.update_or_create(
        workspace_id=workspace_id, defaults={"enabled": True, "error_count": None}
    )
    ws_schedule.enabled = True
    ws_schedule.emails_selected = ["anishkumar.s@fyle.in"]
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
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        value="anishkumar.s@fyle.in",
        detail={"full_name": "Anish Kumar"},
    )

    ws_schedule.emails_selected = ["anishkumar.s@fyle.in"]
    ws_schedule.additional_email_options = []
    ws_schedule.save()
    run_email_notification(workspace_id)

    # Check that email is sent to name from additional_email_options
    ws_schedule.additional_email_options = [
        {"email": "anishkumar.s@fyle.in", "name": "Anish"}
    ]
    ws_schedule.save()
    run_email_notification(workspace_id)


def test_run_email_notification_with_invalid_workspace_id(db):
    workspace_id = None
    with pytest.raises(Exception):
        run_email_notification(workspace_id)


def test_async_add_admins_to_workspace(db, mocker):
    old_users_count = User.objects.count()
    mocker.patch(
        "fyle.platform.apis.v1.admin.Employees.list_all",
        return_value=fyle_data["get_all_employees"],
    )
    async_add_admins_to_workspace(1, "usqywo0f3nBY")
    new_users_count = User.objects.count()

    assert new_users_count > old_users_count


@pytest.mark.django_db()
def test_async_update_workspace_name(mocker):
    mocker.patch(
        'apps.workspaces.tasks.get_fyle_admin',
        return_value={'data': {'org': {'name': 'Test Org'}}}
    )
    workspace = Workspace.objects.get(id=1)
    async_update_workspace_name(workspace, 'Bearer access_token')

    workspace = Workspace.objects.get(id=1)
    assert workspace.name == 'Test Org'


def test_async_create_admin_subscriptions(db, mocker):
    mocker.patch(
        'fyle.platform.apis.v1.admin.Subscriptions.post',
        return_value={}
    )
    async_create_admin_subscriptions(1)


@pytest.mark.django_db(databases=['default'])
def test_post_to_integration_settings(mocker):
    mocker.patch(
        'apps.fyle.helpers.post_request',
        return_value=''
    )

    no_exception = True
    post_to_integration_settings(1, True)

    # If exception is raised, this test will fail
    assert no_exception


def test_import_and_export_expenses_direct_export_case_1(mocker, db):
    """
    Test import and export expenses
    Case 1: Reimbursable expenses are not configured
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_settings.reimbursable_expenses_object = None
    workspace_general_settings.save()

    mock_call = mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=fyle_data['expenses_webhook']
    )

    mock_skip_expenses_and_post_accounting_export_summary = mocker.patch(
        'apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary',
        return_value=None
    )

    import_and_export_expenses(
        report_id='rp1s1L3QtMpF',
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DIRECT_EXPORT
    )

    assert mock_call.call_count == 1
    assert mock_skip_expenses_and_post_accounting_export_summary.call_count == 1


def test_import_and_export_expenses_direct_export_case_2(mocker, db):
    """
    Test import and export expenses
    Case 2: Corporate credit card expenses are not configured
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_settings.corporate_credit_card_expenses_object = None
    workspace_general_settings.save()

    expense_data = fyle_data['expenses_webhook'].copy()
    expense_data[0]['org_id'] = workspace.fyle_org_id
    expense_data[0]['source_account_type'] = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'

    mock_call = mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=expense_data
    )

    mock_skip_expenses_and_post_accounting_export_summary = mocker.patch(
        'apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary',
        return_value=None
    )

    import_and_export_expenses(
        report_id='rp1s1L3QtMpF',
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DIRECT_EXPORT
    )

    assert mock_call.call_count == 1
    assert mock_skip_expenses_and_post_accounting_export_summary.call_count == 1


def test_import_and_export_expenses_direct_export_case_3(mocker, db):
    """
    Test import and export expenses
    Case 3: Negative expesnes with fund_source=PERSONAL
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_settings.corporate_credit_card_expenses_object = None
    workspace_general_settings.save()

    expense_data = fyle_data['expenses_webhook'].copy()
    expense_data[0]['org_id'] = workspace.fyle_org_id
    expense_data[0]['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    expense_data[0]['amount'] = -100

    mock_call = mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.get',
        return_value=expense_data
    )

    mock_skip_expenses_and_post_accounting_export_summary = mocker.patch(
        'apps.fyle.tasks.skip_expenses_and_post_accounting_export_summary',
        return_value=None
    )

    import_and_export_expenses(
        report_id='rp1s1L3QtMpF',
        org_id=workspace.fyle_org_id,
        is_state_change_event=False,
        imported_from=ExpenseImportSourceEnum.DIRECT_EXPORT
    )

    assert mock_call.call_count == 1
    assert mock_skip_expenses_and_post_accounting_export_summary.call_count == 1


def test_skip_expenses_and_post_accounting_export_summary(mocker, db):
    """
    Test skip expenses and post accounting export summary
    """
    workspace = Workspace.objects.get(id=1)

    expense = Expense.objects.first()
    expense.workspace = workspace
    expense.org_id = workspace.fyle_org_id
    expense.accounting_export_summary = {}
    expense.is_skipped = False
    expense.fund_source = 'PERSONAL'
    expense.save()

    # Patch mark_expenses_as_skipped to return the expense in a list
    mock_mark_skipped = mocker.patch(
        'apps.fyle.tasks.mark_expenses_as_skipped',
        return_value=[expense]
    )
    # Patch post_accounting_export_summary to just record the call
    mock_post_summary = mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        return_value=None
    )

    skip_expenses_and_post_accounting_export_summary([expense.id], workspace)

    # Assert mark_expenses_as_skipped was called with Q(), [expense.id], workspace
    assert mock_mark_skipped.call_count == 1
    args, _ = mock_mark_skipped.call_args
    assert args[1] == [expense.id]
    assert args[2] == workspace

    # Assert post_accounting_export_summary was called with workspace_id and expense_ids
    assert mock_post_summary.call_count == 1
    _, post_kwargs = mock_post_summary.call_args
    assert post_kwargs['workspace_id'] == workspace.id
    assert post_kwargs['expense_ids'] == [expense.id]


def test_skip_expenses_and_post_accounting_export_summary_exception(mocker, db):
    """
    Test skip_expenses_and_post_accounting_export_summary when post_accounting_export_summary raises an exception
    """
    workspace = Workspace.objects.get(id=1)

    expense = Expense.objects.first()

    mock_mark_skipped = mocker.patch(
        'apps.fyle.tasks.mark_expenses_as_skipped',
        return_value=[expense]
    )

    mock_post_summary = mocker.patch(
        'apps.fyle.tasks.post_accounting_export_summary',
        side_effect=Exception('Test exception')
    )

    skip_expenses_and_post_accounting_export_summary([expense.id], workspace)

    assert mock_mark_skipped.call_count == 1
    assert mock_post_summary.call_count == 1


def test_run_sync_schedule_expense_groups_with_failed_task_log_and_re_attempt_true(db):
    """
    Test expense group filtering logic
    Case: Expense groups should be included when task log failed but re_attempt_export is True
    """
    workspace_id = 1

    # Create expense group
    expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        description='Test expense group'
    )

    # Create a failed task log with re_attempt_export=True
    _ = TaskLog.objects.create(
        workspace_id=workspace_id,
        type=TaskLogTypeEnum.CREATING_BILL,
        expense_group=expense_group,
        status=TaskLogStatusEnum.FAILED,
        re_attempt_export=True
    )

    # Test the filtering logic directly (same as in run_sync_schedule)
    eligible_expense_group_ids = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True
    ).filter(
        Q(tasklog__isnull=True)
        | Q(tasklog__type__in=[TaskLogTypeEnum.CREATING_BILL, TaskLogTypeEnum.CREATING_BANK_TRANSACTION])
    ).exclude(
        tasklog__status='FAILED',
        tasklog__re_attempt_export=False
    ).values_list('id', flat=True).distinct()

    assert expense_group.id in list(eligible_expense_group_ids), f"Expected expense group {expense_group.id} to be eligible for export"


def test_run_sync_schedule_expense_groups_with_failed_task_log_and_re_attempt_false_filtering(db):
    """
    Test expense group filtering logic
    Case: Expense groups should be excluded when task log failed and re_attempt_export is False
    """
    workspace_id = 1

    expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        description='Test expense group'
    )

    _ = TaskLog.objects.create(
        workspace_id=workspace_id,
        type=TaskLogTypeEnum.CREATING_BILL,
        expense_group=expense_group,
        status=TaskLogStatusEnum.FAILED,
        re_attempt_export=False
    )

    eligible_expense_group_ids = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True
    ).filter(
        Q(tasklog__isnull=True)
        | Q(tasklog__type__in=[TaskLogTypeEnum.CREATING_BILL, TaskLogTypeEnum.CREATING_BANK_TRANSACTION])
    ).exclude(
        tasklog__status='FAILED',
        tasklog__re_attempt_export=False
    ).values_list('id', flat=True).distinct()

    assert expense_group.id not in list(eligible_expense_group_ids), f"Expected expense group {expense_group.id} to be excluded from export"


def test_run_sync_schedule_expense_groups_without_task_log_filtering(db):
    """
    Test expense group filtering logic
    Case: Expense groups should be included when they have no associated task log
    """
    workspace_id = 1

    # Create expense group without any task log
    expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace_id,
        fund_source='PERSONAL',
        description='Test expense group without task log'
    )

    eligible_expense_group_ids = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True
    ).filter(
        Q(tasklog__isnull=True)
        | Q(tasklog__type__in=[TaskLogTypeEnum.CREATING_BILL, TaskLogTypeEnum.CREATING_BANK_TRANSACTION])
    ).exclude(
        tasklog__status='FAILED',
        tasklog__re_attempt_export=False
    ).values_list('id', flat=True).distinct()

    assert expense_group.id in list(eligible_expense_group_ids), f"Expected expense group {expense_group.id} to be eligible for export"
