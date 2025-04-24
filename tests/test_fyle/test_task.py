from unittest import mock

from django.urls import reverse
from fyle.platform.exceptions import InternalServerError
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.fyle.actions import post_accounting_export_summary, update_expenses_in_progress
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.tasks import create_expense_groups, import_and_export_expenses, update_non_exported_expenses
from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings
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

    create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    task_log = TaskLog.objects.get(id=task_log.id)

    assert task_log.status == "COMPLETE"

    fyle_credential = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credential.delete()

    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type="FETCHING_EXPENSES",
        defaults={"status": "IN_PROGRESS"},
    )
    create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status == "FAILED"

    with mock.patch("fyle.platform.apis.v1.admin.Expenses.list_all") as mock_call:
        mock_call.side_effect = FyleInvalidTokenError(
            msg="Invalid Token for Fyle", response="Invalid Token for Fyle"
        )
        create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.delete()

    create_expense_groups(workspace_id, ["PERSONAL", "CCC"], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    task_log = TaskLog.objects.get(id=task_log.id)
    assert task_log.status == "FATAL"

    mock_call.side_effect = InternalServerError('Error')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

    mock_call.side_effect = FyleInvalidTokenError('Invalid Token')
    create_expense_groups(1, ['PERSONAL', 'CCC'], task_log, ExpenseImportSourceEnum.DASHBOARD_SYNC)

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
    post_accounting_export_summary(1)

    assert Expense.objects.filter(id=expense.id).first().accounting_export_summary['synced'] == True


def test_import_and_export_expenses(db, mocker):
    import_and_export_expenses('rp1s1L3QtMpF', 'orPJvXuoLqvJ', False)

    mock_call = mocker.patch('apps.fyle.helpers.get_fund_source')

    import_and_export_expenses('rp1s1L3QtMpF', 'orPJvXuoLqvJ', True, report_state='APPROVED', imported_from=ExpenseImportSourceEnum.WEBHOOK)
    assert mock_call.call_count == 0

    pre_insert_count = Expense.objects.filter(org_id='orPJvXuoLqvJ').count()
    mocker.patch(
        "fyle_integrations_platform_connector.apis.Expenses.get",
        return_value=data["expenses_webhook"],
    )
    import_and_export_expenses('rp1s1L3QtMpF', 'orPJvXuoLqvJ', True, report_state='PAID', imported_from=ExpenseImportSourceEnum.WEBHOOK)
    assert Expense.objects.filter(org_id='orPJvXuoLqvJ').count() > pre_insert_count

    mock_call.side_effect = WorkspaceGeneralSettings.DoesNotExist('Error')
    import_and_export_expenses('rp1s1L3QtMpF', 'orPJvXuoLqvJ', False)

    assert mock_call.call_count == 0


def test_update_non_exported_expenses(db, create_temp_workspace, mocker, api_client, test_connection):
    expense = data['raw_expense']
    default_raw_expense = data['default_raw_expense']
    org_id = expense['org_id']
    payload = {
        "resource": "EXPENSE",
        "action": 'UPDATED_AFTER_APPROVAL',
        "data": expense,
        "reason": 'expense update testing',
    }

    expense_created, _ = Expense.objects.update_or_create(
        org_id=org_id,
        expense_id='txhJLOSKs1iN',
        workspace_id=1,
        defaults=default_raw_expense
    )
    expense_created.accounting_export_summary = {}
    expense_created.save()

    workspace = Workspace.objects.filter(id=1).first()
    workspace.fyle_org_id = org_id
    workspace.save()

    assert expense_created.category == 'Old Category'

    update_non_exported_expenses(payload['data'])

    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'ABN Withholding'

    expense.accounting_export_summary = {"synced": True, "state": "COMPLETE"}
    expense.category = 'Old Category'
    expense.save()

    update_non_exported_expenses(payload['data'])
    expense = Expense.objects.get(expense_id='txhJLOSKs1iN', org_id=org_id)
    assert expense.category == 'Old Category'

    try:
        update_non_exported_expenses(payload['data'])
    except ValidationError as e:
        assert e.detail[0] == 'Workspace mismatch'

    url = reverse('exports', kwargs={'workspace_id': 1})
    response = api_client.post(url, data=payload, format='json')
    assert response.status_code == status.HTTP_200_OK

    url = reverse('exports', kwargs={'workspace_id': 2})
    response = api_client.post(url, data=payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
