from datetime import datetime, timedelta, timezone
from unittest import mock

from django.urls import reverse
from fyle.platform.exceptions import InternalServerError
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_mappings.models import ExpenseAttribute
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.fyle.actions import post_accounting_export_summary, update_expenses_in_progress
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.tasks import (
    check_interval_and_sync_dimension,
    create_expense_groups,
    import_and_export_expenses,
    sync_dimensions,
    update_non_exported_expenses,
)
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


def test_update_non_exported_expenses(db, mocker, api_client, test_connection):
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


def test_check_interval_and_sync_dimension(db, mocker):
    """
    Test check_interval_and_sync_dimension function
    """
    workspace_id = 1

    # Mock sync_dimensions function
    mock_sync_dimensions = mocker.patch('apps.fyle.tasks.sync_dimensions')

    # Test case 1: workspace.source_synced_at is None - should call sync_dimensions
    workspace = Workspace.objects.get(id=workspace_id)
    workspace.source_synced_at = None
    workspace.save()

    check_interval_and_sync_dimension(workspace_id)

    # Verify sync_dimensions was called
    mock_sync_dimensions.assert_called_once_with(workspace_id)
    mock_sync_dimensions.reset_mock()

    # Test case 2: workspace.source_synced_at exists and time interval > 0 days - should call sync_dimensions
    workspace.source_synced_at = datetime.now(timezone.utc) - timedelta(days=2)
    workspace.save()

    check_interval_and_sync_dimension(workspace_id)

    # Verify sync_dimensions was called
    mock_sync_dimensions.assert_called_once_with(workspace_id)
    mock_sync_dimensions.reset_mock()

    # Test case 3: workspace.source_synced_at exists and time interval <= 0 days - should NOT call sync_dimensions
    workspace.source_synced_at = datetime.now(timezone.utc) - timedelta(hours=12)  # Less than 1 day
    workspace.save()

    check_interval_and_sync_dimension(workspace_id)

    # Verify sync_dimensions was NOT called
    mock_sync_dimensions.assert_not_called()


def test_sync_dimensions(db, mocker):
    """
    Test sync_dimensions function
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    # Create WorkspaceGeneralSettings
    workspace_general_settings, _ = WorkspaceGeneralSettings.objects.get_or_create(
        workspace_id=workspace_id,
        defaults={
            'corporate_credit_card_expenses_object': 'BANK TRANSACTION'
        }
    )

    # Create some test ExpenseAttribute objects for unmapped cards
    ExpenseAttribute.objects.create(
        attribute_type="CORPORATE_CARD",
        workspace_id=workspace_id,
        active=True,
        value="Test Card 1",
        source_id="card1"
    )
    ExpenseAttribute.objects.create(
        attribute_type="CORPORATE_CARD",
        workspace_id=workspace_id,
        active=True,
        value="Test Card 2",
        source_id="card2"
    )

    # Mock PlatformConnector and its methods
    mock_platform = mocker.MagicMock()
    mock_platform.categories.get_count.return_value = 5
    mock_platform.categories.sync.return_value = None
    mock_platform.projects.get_count.return_value = 3
    mock_platform.projects.sync.return_value = None
    mocker.patch('apps.fyle.tasks.PlatformConnector', return_value=mock_platform)

    # Mock patch_integration_settings_for_unmapped_cards
    mock_patch_settings = mocker.MagicMock()
    mocker.patch('apps.fyle.tasks.import_string', return_value=mock_patch_settings)

    # Create some ExpenseAttribute objects for categories and projects
    ExpenseAttribute.objects.create(
        attribute_type="CATEGORY",
        workspace_id=workspace_id,
        active=True,
        value="Test Category",
        source_id="cat1"
    )
    ExpenseAttribute.objects.create(
        attribute_type="PROJECT",
        workspace_id=workspace_id,
        active=True,
        value="Test Project",
        source_id="proj1"
    )

    # Test case 1: sync_dimensions with is_export=False
    original_source_synced_at = workspace.source_synced_at

    sync_dimensions(workspace_id, is_export=False)

    # Verify workspace.source_synced_at was updated
    workspace.refresh_from_db()
    assert workspace.source_synced_at != original_source_synced_at
    assert workspace.source_synced_at is not None

    # Verify patch_integration_settings_for_unmapped_cards was called with correct count
    mock_patch_settings.assert_called_once_with(workspace_id=workspace_id, unmapped_card_count=2)
    mock_patch_settings.reset_mock()

    # Test case 2: sync_dimensions with is_export=True and category count mismatch
    sync_dimensions(workspace_id, is_export=True)

    # Verify categories.sync was called due to count mismatch (5 vs 1)
    mock_platform.categories.sync.assert_called_once()

    # Verify projects.sync was called due to count mismatch (3 vs 1)
    mock_platform.projects.sync.assert_called_once()

    # Verify workspace.source_synced_at was updated again
    updated_source_synced_at = workspace.source_synced_at
    workspace.refresh_from_db()
    assert workspace.source_synced_at != updated_source_synced_at

    # Test case 3: sync_dimensions without corporate_credit_card_expenses_object
    workspace_general_settings.corporate_credit_card_expenses_object = None
    workspace_general_settings.save()
    mock_patch_settings.reset_mock()

    sync_dimensions(workspace_id, is_export=False)

    # Verify patch_integration_settings_for_unmapped_cards was NOT called
    mock_patch_settings.assert_not_called()

    # Test case 4: sync_dimensions without WorkspaceGeneralSettings
    workspace_general_settings.delete()
    mock_patch_settings.reset_mock()

    sync_dimensions(workspace_id, is_export=False)

    # Verify patch_integration_settings_for_unmapped_cards was NOT called
    mock_patch_settings.assert_not_called()
