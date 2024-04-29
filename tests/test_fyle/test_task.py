from unittest import mock

from fyle.platform.exceptions import (
    InvalidTokenError as FyleInvalidTokenError,
    InternalServerError
)
from apps.fyle.actions import update_expenses_in_progress
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.tasks import create_expense_groups, import_and_export_expenses, post_accounting_export_summary
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings
from tests.test_fyle.fixtures import data


def test_create_expense_groups(mocker, db):
    workspace_id = 1

    mock_call = mocker.patch(
        "fyle_integrations_platform_connector.apis.Expenses.get",
        return_value=data["expenses"],
    )

    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type="FETCHING_EXPENSES",
        defaults={"status": "IN_PROGRESS"},
    )

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.reimbursable_export_date_type = "last_spent_at"
    expense_group_settings.ccc_export_date_type = "last_spent_at"
    expense_group_settings.save()

    create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log)

    task_log = TaskLog.objects.get(id=task_log.id)

    assert task_log.status == "COMPLETE"

    fyle_credential = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credential.delete()

    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type="FETCHING_EXPENSES",
        defaults={"status": "IN_PROGRESS"},
    )
    create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status == "FAILED"

    with mock.patch("fyle.platform.apis.v1beta.admin.Expenses.list_all") as mock_call:
        mock_call.side_effect = FyleInvalidTokenError(
            msg="Invalid Token for Fyle", response="Invalid Token for Fyle"
        )
        create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log)

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.delete()

    create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status == "FATAL"

    mock_call.side_effect = InternalServerError('Error')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    mock_call.side_effect = FyleInvalidTokenError('Invalid Token')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log)

    mock_call.call_count = 2


def test_post_accounting_export_summary(db, mocker):
    expense_group = ExpenseGroup.objects.filter(workspace_id=1).first()
    expense = expense_group.expenses.first()
    expense_group.expenses.remove(expense.id)

    expense = Expense.objects.filter(id=expense.id).first()
    expense.workspace_id = 1
    expense.save()

    update_expenses_in_progress([expense])

    assert Expense.objects.filter(id=expense.id).first().accounting_export_summary['synced'] == False

    mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.post_bulk_accounting_export_summary',
        return_value=[]
    )
    post_accounting_export_summary('orPJvXuoLqvJ', 1)

    assert Expense.objects.filter(id=expense.id).first().accounting_export_summary['synced'] == True


def test_import_and_export_expenses(db, mocker):
    import_and_export_expenses('rp1s1L3QtMpF', 'orPJvXuoLqvJ')

    mock_call = mocker.patch('apps.fyle.helpers.get_fund_source')
    mock_call.side_effect = WorkspaceGeneralSettings.DoesNotExist('Error')
    import_and_export_expenses('rp1s1L3QtMpF', 'orPJvXuoLqvJ')

    assert mock_call.call_count == 0
