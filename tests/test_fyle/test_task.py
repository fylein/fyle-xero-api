from unittest import mock

from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError

from apps.fyle.models import ExpenseGroupSettings, Expense, ExpenseGroup
from django.db.models import Q
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, Workspace
from tests.test_fyle.fixtures import data
from apps.fyle.tasks import create_expense_groups, post_accounting_export_summary
from apps.fyle.actions import update_failed_expenses


def test_create_expense_groups(mocker, db):
    workspace_id = 1

    mocker.patch(
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


def test_post_accounting_export_summary(db, mocker):
    expense_group = ExpenseGroup.objects.filter(workspace_id=1).first()
    expense_id = expense_group.expenses.first().id
    expense_group.expenses.remove(expense_id)

    workspace = Workspace.objects.get(id=1)

    expense = Expense.objects.filter(id=expense_id).first()
    expense.workspace_id = 1
    expense.save()

    update_failed_expenses(Q(), [expense_id], workspace)

    assert Expense.objects.filter(id=expense_id).first().accounting_export_summary['synced'] == False

    mocker.patch(
        'fyle_integrations_platform_connector.apis.Expenses.post_bulk_accounting_export_summary',
        return_value=[]
    )
    post_accounting_export_summary('orPJvXuoLqvJ', 1)

    assert Expense.objects.filter(id=expense_id).first().accounting_export_summary['synced'] == True
