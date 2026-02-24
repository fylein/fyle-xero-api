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
from apps.fyle.enums import FundSourceEnum
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.fyle.tasks import (
    _delete_expense_groups_for_report,
    _handle_expense_ejected_from_report,
    check_interval_and_sync_dimension,
    cleanup_scheduled_task,
    construct_filter_for_affected_expense_groups,
    create_expense_groups,
    delete_expense_group_and_related_data,
    delete_expenses_in_db,
    get_grouping_types,
    handle_category_changes_for_expense,
    handle_expense_fund_source_change,
    handle_expense_report_change,
    handle_fund_source_changes_for_expense_ids,
    handle_org_setting_updated,
    import_and_export_expenses,
    process_expense_group_for_fund_source_update,
    recreate_expense_groups,
    schedule_task_for_expense_group_fund_source_change,
    sync_dimensions,
    update_non_exported_expenses,
)
from apps.tasks.models import Error, TaskLog
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


def test_import_and_export_expenses_state_change_real_time_export_disabled(db, mocker):
    mocker.patch(
        "fyle_integrations_platform_connector.apis.Expenses.get",
        return_value=data["expenses_webhook"],
    )
    mock_export = mocker.patch('apps.fyle.tasks.export_to_xero')

    workspace = Workspace.objects.get(fyle_org_id='orPJvXuoLqvJ')

    expense = Expense.objects.create(
        workspace_id=workspace.id,
        expense_id='txTestRealTime',
        employee_email='test@test.com',
        category='Test',
        amount=100,
        currency='USD',
        org_id='orPJvXuoLqvJ',
        report_id='rpTestRT',
        spent_at='2024-01-01T00:00:00Z',
        expense_created_at='2024-01-01T00:00:00Z',
        expense_updated_at='2024-01-01T00:00:00Z',
        fund_source='PERSONAL'
    )

    expense_group = ExpenseGroup.objects.create(
        workspace=workspace,
        fund_source='PERSONAL',
        description={},
        exported_at=None
    )
    expense_group.expenses.add(expense)

    import_and_export_expenses(
        'rpTestRT', 'orPJvXuoLqvJ', True,
        report_state='PAID',
        imported_from=ExpenseImportSourceEnum.WEBHOOK
    )

    mock_export.assert_not_called()


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


def test_handle_expense_fund_source_change(db, mocker):
    """
    Test handle_expense_fund_source_change function
    """
    # Use fixtures for test data
    test_data = data['fund_source_change']
    constants = test_data['test_constants']

    workspace_id = constants['workspace_id']
    report_id = constants['report_id']

    # Create test expenses in database using fixture data
    expense1, _ = Expense.objects.update_or_create(
        expense_id=constants['expense_id'],
        workspace_id=workspace_id,
        defaults=test_data['expense_defaults']
    )

    # Mock platform expenses using fixture data
    mock_platform = mocker.MagicMock()
    mock_platform.expenses.get.return_value = [test_data['mock_platform_expense_ccc']]

    # Mock dependencies
    mock_handle_fund_source_changes = mocker.patch('apps.fyle.tasks.handle_fund_source_changes_for_expense_ids')
    mocker.patch('apps.fyle.models.Expense.create_expense_objects')

    handle_expense_fund_source_change(workspace_id, report_id, mock_platform)

    # Verify that handle_fund_source_changes_for_expense_ids was called
    mock_handle_fund_source_changes.assert_called_once()
    call_args = mock_handle_fund_source_changes.call_args
    assert call_args[1]['workspace_id'] == workspace_id
    assert call_args[1]['report_id'] == report_id
    assert len(call_args[1]['changed_expense_ids']) == 1
    assert call_args[1]['affected_fund_source_expense_ids'][FundSourceEnum.PERSONAL] == [expense1.id]


def test_handle_expense_fund_source_change_no_changes(db, mocker):
    """
    Test handle_expense_fund_source_change function when no fund source changes
    """
    # Use fixtures for test data
    test_data = data['fund_source_change']
    constants = test_data['test_constants']

    workspace_id = constants['workspace_id']
    report_id = constants['report_id']

    # Create test expenses in database using fixture data
    Expense.objects.update_or_create(
        expense_id=constants['expense_id'],
        workspace_id=workspace_id,
        defaults=test_data['expense_defaults']
    )

    # Mock platform expenses - no fund source change
    mock_platform = mocker.MagicMock()
    mock_platform.expenses.get.return_value = [test_data['mock_platform_expense_personal']]

    # Mock dependencies
    mock_handle_fund_source_changes = mocker.patch('apps.fyle.tasks.handle_fund_source_changes_for_expense_ids')

    handle_expense_fund_source_change(workspace_id, report_id, mock_platform)

    # Verify that handle_fund_source_changes_for_expense_ids was NOT called
    mock_handle_fund_source_changes.assert_not_called()


def test_update_non_exported_expenses_with_fund_source_change(db, mocker):
    test_data = data['fund_source_change']

    workspace, _ = Workspace.objects.update_or_create(
        **test_data['workspace_defaults']
    )

    expense_defaults = test_data['expense_defaults'].copy()
    expense_defaults['accounting_export_summary'] = {'state': 'NOT_EXPORTED'}

    expense, _ = Expense.objects.update_or_create(
        expense_id=test_data['test_constants']['expense_id'],
        workspace_id=workspace.id,
        defaults=expense_defaults
    )

    mock_fyle_expenses = mocker.MagicMock()
    mock_fyle_expenses.construct_expense_object.return_value = [
        {
            'source_account_type': 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT',
            'category': expense.category,
            'sub_category': expense.sub_category
        }
    ]
    mocker.patch('apps.fyle.tasks.FyleExpenses', return_value=mock_fyle_expenses)

    mock_handle_fund_source_changes = mocker.patch('apps.fyle.tasks.handle_fund_source_changes_for_expense_ids')
    mocker.patch('apps.fyle.models.Expense.create_expense_objects')

    update_non_exported_expenses(test_data['expense_payload'])

    mock_handle_fund_source_changes.assert_called_once()


def test_get_grouping_types(db):
    """
    Test get_grouping_types function
    """
    # Use fixtures for test data
    test_data = data['fund_source_change']
    workspace_id = test_data['test_constants']['workspace_id']

    # Create ExpenseGroupSettings using fixture data
    expense_group_settings, _ = ExpenseGroupSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults=test_data['expense_group_settings_defaults']
    )

    grouping_types = get_grouping_types(workspace_id)

    assert grouping_types[FundSourceEnum.PERSONAL] == 'report'
    assert grouping_types[FundSourceEnum.CCC] == 'expense'

    # Test with no ExpenseGroupSettings
    expense_group_settings.delete()
    grouping_types = get_grouping_types(workspace_id)
    assert grouping_types == {}


def test_construct_filter_for_affected_expense_groups(db):
    """
    Test construct_filter_for_affected_expense_groups function
    """
    workspace_id = 1
    report_id = 'rp1s1L3QtMpF'
    changed_expense_ids = [1, 2, 3]
    affected_fund_source_expense_ids = {
        FundSourceEnum.PERSONAL: [1, 2],
        FundSourceEnum.CCC: [3]
    }

    # Create ExpenseGroupSettings with both report grouping
    ExpenseGroupSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expense_group_fields': ['employee_email', 'report_id'],
            'corporate_credit_card_expense_group_fields': ['employee_email', 'report_id']
        }
    )

    filter_query = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    # The filter should be for report_id when both are report-based grouping
    assert filter_query is not None

    # Test with both expense grouping
    ExpenseGroupSettings.objects.filter(workspace_id=workspace_id).update(
        reimbursable_expense_group_fields=['employee_email', 'expense_id'],
        corporate_credit_card_expense_group_fields=['employee_email', 'expense_id']
    )

    filter_query = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    # The filter should be for expense IDs when both are expense-based grouping
    assert filter_query is not None


def test_handle_fund_source_changes_for_expense_ids_no_affected_groups(db, mocker):
    """
    Test handle_fund_source_changes_for_expense_ids when no affected groups are found
    """
    workspace_id = 1
    changed_expense_ids = [1, 2]
    report_id = 'rp1s1L3QtMpF'
    affected_fund_source_expense_ids = {FundSourceEnum.PERSONAL: [1, 2]}

    # Mock ExpenseGroup.objects.filter to return empty queryset
    mock_expense_groups = mocker.patch('apps.fyle.models.ExpenseGroup.objects.filter')
    mock_expense_groups.return_value.annotate.return_value.distinct.return_value = []

    # Mock construct_filter_for_affected_expense_groups
    mock_construct_filter = mocker.patch('apps.fyle.tasks.construct_filter_for_affected_expense_groups')
    mock_construct_filter.return_value = mocker.MagicMock()

    handle_fund_source_changes_for_expense_ids(
        workspace_id=workspace_id,
        changed_expense_ids=changed_expense_ids,
        report_id=report_id,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    # Verify that construct_filter was called
    mock_construct_filter.assert_called_once()


def test_handle_fund_source_changes_for_expense_ids_with_groups(db, mocker):
    """
    Test handle_fund_source_changes_for_expense_ids with affected groups
    """
    workspace_id = 1
    changed_expense_ids = [1, 2]
    report_id = 'rp1s1L3QtMpF'
    affected_fund_source_expense_ids = {FundSourceEnum.PERSONAL: [1, 2]}

    # Create mock expense groups
    mock_group1 = mocker.MagicMock()
    mock_group1.id = 1
    mock_group1.expense_count = 2
    mock_group2 = mocker.MagicMock()
    mock_group2.id = 2
    mock_group2.expense_count = 1

    # Mock ExpenseGroup.objects.filter
    mock_expense_groups = mocker.patch('apps.fyle.models.ExpenseGroup.objects.filter')

    # Create the final queryset that will be returned by annotate().distinct()
    mock_final_queryset = mocker.MagicMock()
    mock_final_queryset.__iter__ = mocker.MagicMock(return_value=iter([mock_group1, mock_group2]))
    mock_final_queryset.__bool__ = mocker.MagicMock(return_value=True)
    mock_final_queryset.values_list.return_value = [1, 2, 3, 4]  # affected expense IDs

    # Setup the chain of calls
    mock_queryset = mocker.MagicMock()
    mock_queryset.annotate.return_value.distinct.return_value = mock_final_queryset
    mock_expense_groups.return_value = mock_queryset

    # Mock construct_filter_for_affected_expense_groups
    mock_construct_filter = mocker.patch('apps.fyle.tasks.construct_filter_for_affected_expense_groups')
    mock_construct_filter.return_value = mocker.MagicMock()

    # Mock process_expense_group_for_fund_source_update to return True (processed)
    mock_process_group = mocker.patch('apps.fyle.tasks.process_expense_group_for_fund_source_update')
    mock_process_group.return_value = True

    # Mock recreate_expense_groups
    mock_recreate = mocker.patch('apps.fyle.tasks.recreate_expense_groups')

    # Mock cleanup_scheduled_task
    mock_cleanup = mocker.patch('apps.fyle.tasks.cleanup_scheduled_task')

    handle_fund_source_changes_for_expense_ids(
        workspace_id=workspace_id,
        changed_expense_ids=changed_expense_ids,
        report_id=report_id,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    # Verify all groups were processed
    assert mock_process_group.call_count == 2
    mock_recreate.assert_called_once_with(workspace_id=workspace_id, expense_ids=[1, 2, 3, 4])
    mock_cleanup.assert_called_once_with(task_name=None, workspace_id=workspace_id)


def test_handle_fund_source_changes_for_expense_ids_mixed_processing(db, mocker):
    """
    Test handle_fund_source_changes_for_expense_ids with mixed processing results
    """

    workspace_id = 1
    changed_expense_ids = [1, 2]
    report_id = 'rp1s1L3QtMpF'
    affected_fund_source_expense_ids = {FundSourceEnum.PERSONAL: [1, 2]}

    # Create mock expense groups
    mock_group1 = mocker.MagicMock()
    mock_group1.id = 1
    mock_group1.expense_count = 2
    mock_group2 = mocker.MagicMock()
    mock_group2.id = 2
    mock_group2.expense_count = 1

    # Mock ExpenseGroup.objects.filter
    mock_expense_groups = mocker.patch('apps.fyle.models.ExpenseGroup.objects.filter')

    # Create the final queryset that will be returned by annotate().distinct()
    mock_final_queryset = mocker.MagicMock()
    mock_final_queryset.__iter__ = mocker.MagicMock(return_value=iter([mock_group1, mock_group2]))
    mock_final_queryset.__bool__ = mocker.MagicMock(return_value=True)
    mock_final_queryset.values_list.return_value = [1, 2, 3, 4]

    # Setup the chain of calls
    mock_queryset = mocker.MagicMock()
    mock_queryset.annotate.return_value.distinct.return_value = mock_final_queryset
    mock_expense_groups.return_value = mock_queryset

    # Mock construct_filter_for_affected_expense_groups
    mock_construct_filter = mocker.patch('apps.fyle.tasks.construct_filter_for_affected_expense_groups')
    mock_construct_filter.return_value = mocker.MagicMock()

    # Mock process_expense_group_for_fund_source_update - first returns True, second returns False
    mock_process_group = mocker.patch('apps.fyle.tasks.process_expense_group_for_fund_source_update')
    mock_process_group.side_effect = [True, False]

    # Mock recreate_expense_groups (should not be called)
    mock_recreate = mocker.patch('apps.fyle.tasks.recreate_expense_groups')

    # Mock cleanup_scheduled_task (should not be called)
    mock_cleanup = mocker.patch('apps.fyle.tasks.cleanup_scheduled_task')

    handle_fund_source_changes_for_expense_ids(
        workspace_id=workspace_id,
        changed_expense_ids=changed_expense_ids,
        report_id=report_id,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    # Verify all groups were processed but recreation was skipped
    assert mock_process_group.call_count == 2
    mock_recreate.assert_not_called()
    mock_cleanup.assert_not_called()


def test_process_expense_group_for_fund_source_update_no_task_log(db, mocker):
    """
    Test process_expense_group_for_fund_source_update when no task log exists
    """

    # Create mock expense group
    mock_expense_group = mocker.MagicMock()
    mock_expense_group.id = 1
    mock_expense_group.workspace_id = 1

    # Mock TaskLog.objects.select_for_update().filter() to return None
    mock_task_log = mocker.patch('apps.tasks.models.TaskLog.objects.select_for_update')
    mock_task_log.return_value.filter.return_value.order_by.return_value.first.return_value = None

    # Mock delete_expense_group_and_related_data
    mock_delete = mocker.patch('apps.fyle.tasks.delete_expense_group_and_related_data')

    result = process_expense_group_for_fund_source_update(
        expense_group=mock_expense_group,
        changed_expense_ids=[1, 2],
        workspace_id=1,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={FundSourceEnum.PERSONAL: [1, 2]}
    )

    assert result is True
    mock_delete.assert_called_once_with(expense_group=mock_expense_group, workspace_id=1)


def test_process_expense_group_for_fund_source_update_enqueued_task(db, mocker):
    """
    Test process_expense_group_for_fund_source_update when task is enqueued
    """

    # Create mock expense group
    mock_expense_group = mocker.MagicMock()
    mock_expense_group.id = 1
    mock_expense_group.workspace_id = 1

    # Create mock task log with ENQUEUED status
    mock_task_log_obj = mocker.MagicMock()
    mock_task_log_obj.status = 'ENQUEUED'

    # Mock TaskLog.objects.select_for_update().filter()
    mock_task_log = mocker.patch('apps.tasks.models.TaskLog.objects.select_for_update')
    mock_task_log.return_value.filter.return_value.order_by.return_value.first.return_value = mock_task_log_obj

    # Mock schedule_task_for_expense_group_fund_source_change
    mock_schedule = mocker.patch('apps.fyle.tasks.schedule_task_for_expense_group_fund_source_change')

    result = process_expense_group_for_fund_source_update(
        expense_group=mock_expense_group,
        changed_expense_ids=[1, 2],
        workspace_id=1,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={FundSourceEnum.PERSONAL: [1, 2]}
    )

    assert result is False
    mock_schedule.assert_called_once()


def test_process_expense_group_for_fund_source_update_in_progress_task(db, mocker):
    """
    Test process_expense_group_for_fund_source_update when task is in progress
    """

    # Create mock expense group
    mock_expense_group = mocker.MagicMock()
    mock_expense_group.id = 1
    mock_expense_group.workspace_id = 1

    # Create mock task log with IN_PROGRESS status
    mock_task_log_obj = mocker.MagicMock()
    mock_task_log_obj.status = 'IN_PROGRESS'

    # Mock TaskLog.objects.select_for_update().filter()
    mock_task_log = mocker.patch('apps.tasks.models.TaskLog.objects.select_for_update')
    mock_task_log.return_value.filter.return_value.order_by.return_value.first.return_value = mock_task_log_obj

    # Mock schedule_task_for_expense_group_fund_source_change
    mock_schedule = mocker.patch('apps.fyle.tasks.schedule_task_for_expense_group_fund_source_change')

    result = process_expense_group_for_fund_source_update(
        expense_group=mock_expense_group,
        changed_expense_ids=[1, 2],
        workspace_id=1,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={FundSourceEnum.PERSONAL: [1, 2]}
    )

    assert result is False
    mock_schedule.assert_called_once()


def test_process_expense_group_for_fund_source_update_complete_task(db, mocker):
    """
    Test process_expense_group_for_fund_source_update when task is complete
    """

    # Create mock expense group
    mock_expense_group = mocker.MagicMock()
    mock_expense_group.id = 1
    mock_expense_group.workspace_id = 1

    # Create mock task log with COMPLETE status
    mock_task_log_obj = mocker.MagicMock()
    mock_task_log_obj.status = 'COMPLETE'

    # Mock TaskLog.objects.select_for_update().filter()
    mock_task_log = mocker.patch('apps.tasks.models.TaskLog.objects.select_for_update')
    mock_task_log.return_value.filter.return_value.order_by.return_value.first.return_value = mock_task_log_obj

    result = process_expense_group_for_fund_source_update(
        expense_group=mock_expense_group,
        changed_expense_ids=[1, 2],
        workspace_id=1,
        report_id='rp1s1L3QtMpF',
        affected_fund_source_expense_ids={FundSourceEnum.PERSONAL: [1, 2]}
    )

    assert result is False


def test_delete_expense_group_and_related_data(db, mocker):
    """
    Test delete_expense_group_and_related_data function
    """

    # Create mock expense group
    mock_expense_group = mocker.MagicMock()
    mock_expense_group.id = 123
    mock_expense_group.delete = mocker.MagicMock()

    # Mock TaskLog.objects.filter().delete()
    mock_task_log_delete = mocker.MagicMock()
    mock_task_log_delete.return_value = (5, {})  # 5 task logs deleted
    mock_task_log = mocker.patch('apps.tasks.models.TaskLog.objects.filter')
    mock_task_log.return_value.delete = mock_task_log_delete

    # Mock Error.objects.filter().delete() - first call for direct deletion
    mock_error_delete = mocker.MagicMock()
    mock_error_delete.return_value = (2, {})  # 2 errors deleted

    # Mock Error.objects.filter() for mapping_error_expense_group_ids - second call
    mock_error_obj1 = mocker.MagicMock()
    mock_error_obj1.id = 1
    mock_error_obj1.mapping_error_expense_group_ids = mocker.MagicMock()
    mock_error_obj1.mapping_error_expense_group_ids.__bool__ = mocker.MagicMock(return_value=True)  # Has items after remove
    mock_error_obj1.save = mocker.MagicMock()

    mock_error_obj2 = mocker.MagicMock()
    mock_error_obj2.id = 2
    mock_error_obj2.mapping_error_expense_group_ids = mocker.MagicMock()
    mock_error_obj2.mapping_error_expense_group_ids.__bool__ = mocker.MagicMock(return_value=False)  # Empty after remove
    mock_error_obj2.delete = mocker.MagicMock()

    # Mock both calls to Error.objects.filter
    mock_error = mocker.patch('apps.tasks.models.Error.objects.filter')
    mock_error.side_effect = [
        mocker.MagicMock(delete=mock_error_delete),  # First call - direct deletion
        [mock_error_obj1, mock_error_obj2]           # Second call - mapping errors
    ]

    delete_expense_group_and_related_data(expense_group=mock_expense_group, workspace_id=1)

    # Verify all deletions were called
    mock_task_log.assert_called_once()
    mock_task_log_delete.assert_called_once()
    mock_error_delete.assert_called_once()
    mock_expense_group.delete.assert_called_once()

    # Verify mapping error handling
    mock_error_obj1.mapping_error_expense_group_ids.remove.assert_called_once_with(123)
    mock_error_obj1.save.assert_called_once()
    mock_error_obj2.mapping_error_expense_group_ids.remove.assert_called_once_with(123)
    mock_error_obj2.delete.assert_called_once()


def test_recreate_expense_groups_no_expenses(db, mocker):
    """
    Test recreate_expense_groups when no expenses are found
    """

    # Mock Expense.objects.filter to return empty queryset
    mock_expenses = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expenses.return_value = []

    recreate_expense_groups(workspace_id=1, expense_ids=[1, 2, 3])

    mock_expenses.assert_called_once()


def test_recreate_expense_groups_with_expenses(db, mocker):
    """
    Test recreate_expense_groups with expenses
    """

    # Create mock expenses
    mock_expense1 = mocker.MagicMock()
    mock_expense1.id = 1
    mock_expense1.fund_source = FundSourceEnum.PERSONAL

    mock_expense2 = mocker.MagicMock()
    mock_expense2.id = 2
    mock_expense2.fund_source = FundSourceEnum.CCC

    # Mock Expense.objects.filter
    mock_expenses = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expenses.return_value = [mock_expense1, mock_expense2]

    # Mock WorkspaceGeneralSettings
    mock_config = mocker.MagicMock()
    mock_config.reimbursable_expenses_object = 'BILL'
    mock_config.corporate_credit_card_expenses_object = 'BANK_TRANSACTION'
    mock_workspace_settings = mocker.patch('apps.workspaces.models.WorkspaceGeneralSettings.objects.get')
    mock_workspace_settings.return_value = mock_config

    # Mock ExpenseGroup.create_expense_groups_by_report_id_fund_source
    mock_create_groups = mocker.patch('apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source')

    recreate_expense_groups(workspace_id=1, expense_ids=[1, 2])

    # Verify expense group creation was called
    mock_create_groups.assert_called_once_with([mock_expense1, mock_expense2], 1)


def test_recreate_expense_groups_filter_reimbursable(db, mocker):
    """
    Test recreate_expense_groups filtering out reimbursable expenses when not configured
    """

    # Create mock expenses
    mock_expense1 = mocker.MagicMock()
    mock_expense1.id = 1
    mock_expense1.fund_source = FundSourceEnum.PERSONAL

    mock_expense2 = mocker.MagicMock()
    mock_expense2.id = 2
    mock_expense2.fund_source = FundSourceEnum.CCC

    # Mock Expense.objects.filter
    mock_expenses = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expenses.return_value = [mock_expense1, mock_expense2]

    # Mock WorkspaceGeneralSettings - no reimbursable expenses configured
    mock_config = mocker.MagicMock()
    mock_config.reimbursable_expenses_object = None
    mock_config.corporate_credit_card_expenses_object = 'BANK_TRANSACTION'
    mock_workspace_settings = mocker.patch('apps.workspaces.models.WorkspaceGeneralSettings.objects.get')
    mock_workspace_settings.return_value = mock_config

    # Mock delete_expenses_in_db
    mock_delete = mocker.patch('apps.fyle.tasks.delete_expenses_in_db')

    # Mock ExpenseGroup.create_expense_groups_by_report_id_fund_source
    mock_create_groups = mocker.patch('apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source')

    recreate_expense_groups(workspace_id=1, expense_ids=[1, 2])

    # Verify reimbursable expense was deleted
    mock_delete.assert_called_once_with(expense_ids=[1], workspace_id=1)
    # Verify only CCC expense was passed to group creation
    mock_create_groups.assert_called_once_with([mock_expense2], 1)


def test_recreate_expense_groups_filter_ccc(db, mocker):
    """
    Test recreate_expense_groups filtering out CCC expenses when not configured
    """

    # Create mock expenses
    mock_expense1 = mocker.MagicMock()
    mock_expense1.id = 1
    mock_expense1.fund_source = FundSourceEnum.PERSONAL

    mock_expense2 = mocker.MagicMock()
    mock_expense2.id = 2
    mock_expense2.fund_source = FundSourceEnum.CCC

    # Mock Expense.objects.filter
    mock_expenses = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expenses.return_value = [mock_expense1, mock_expense2]

    # Mock WorkspaceGeneralSettings - no CCC expenses configured
    mock_config = mocker.MagicMock()
    mock_config.reimbursable_expenses_object = 'BILL'
    mock_config.corporate_credit_card_expenses_object = None
    mock_workspace_settings = mocker.patch('apps.workspaces.models.WorkspaceGeneralSettings.objects.get')
    mock_workspace_settings.return_value = mock_config

    # Mock delete_expenses_in_db
    mock_delete = mocker.patch('apps.fyle.tasks.delete_expenses_in_db')

    # Mock ExpenseGroup.create_expense_groups_by_report_id_fund_source
    mock_create_groups = mocker.patch('apps.fyle.models.ExpenseGroup.create_expense_groups_by_report_id_fund_source')

    recreate_expense_groups(workspace_id=1, expense_ids=[1, 2])

    # Verify CCC expense was deleted
    mock_delete.assert_called_once_with(expense_ids=[2], workspace_id=1)
    # Verify only reimbursable expense was passed to group creation
    mock_create_groups.assert_called_once_with([mock_expense1], 1)


def test_delete_expenses_in_db(db, mocker):
    """
    Test delete_expenses_in_db function
    """

    # Mock Expense.objects.filter().delete()
    mock_delete = mocker.MagicMock()
    mock_delete.return_value = (3, {})  # 3 expenses deleted
    mock_expenses = mocker.patch('apps.fyle.models.Expense.objects.filter')
    mock_expenses.return_value.delete = mock_delete

    delete_expenses_in_db(expense_ids=[1, 2, 3], workspace_id=1)

    mock_expenses.assert_called_once_with(id__in=[1, 2, 3], workspace_id=1)
    mock_delete.assert_called_once()


def test_schedule_task_for_expense_group_fund_source_change_no_django_q(db, mocker):
    """
    Test schedule_task_for_expense_group_fund_source_change when Django Q is not available
    """

    # Mock the import to raise ImportError
    with mocker.patch('django_q.models.Schedule', side_effect=ImportError):
        with mocker.patch('django_q.tasks.schedule', side_effect=ImportError):
            # Should not raise an error, just log a warning
            schedule_task_for_expense_group_fund_source_change(
                changed_expense_ids=[1, 2],
                workspace_id=1,
                report_id='rp1s1L3QtMpF',
                affected_fund_source_expense_ids={FundSourceEnum.PERSONAL: [1, 2]}
            )


def test_cleanup_scheduled_task_no_django_q(db, mocker):
    """
    Test cleanup_scheduled_task when Django Q is not available
    """

    # Mock the import to raise ImportError
    with mocker.patch('django_q.models.Schedule', side_effect=ImportError):
        # Should not raise an error, just log a warning
        cleanup_scheduled_task(task_name='test_task', workspace_id=1)


def test_cleanup_scheduled_task_with_task(db, mocker):
    """
    Test cleanup_scheduled_task when task exists
    """

    # Mock Schedule model
    mock_schedule_obj = mocker.MagicMock()
    mock_schedule_obj.delete = mocker.MagicMock()

    mock_schedule = mocker.MagicMock()
    mock_schedule.objects.filter.return_value.first.return_value = mock_schedule_obj

    # Patch the dynamic import within the function
    with mocker.patch('django_q.models.Schedule', mock_schedule):
        cleanup_scheduled_task(task_name='test_task', workspace_id=1)

    mock_schedule.objects.filter.assert_called_once_with(
        name='test_task',
        func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids'
    )
    mock_schedule_obj.delete.assert_called_once()


def test_cleanup_scheduled_task_no_task(db, mocker):
    """
    Test cleanup_scheduled_task when no task exists
    """

    # Mock Schedule model
    mock_schedule = mocker.MagicMock()
    mock_schedule.objects.filter.return_value.first.return_value = None

    # Patch the dynamic import within the function
    with mocker.patch('django_q.models.Schedule', mock_schedule):
        cleanup_scheduled_task(task_name='test_task', workspace_id=1)

    mock_schedule.objects.filter.assert_called_once_with(
        name='test_task',
        func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids'
    )


def test_construct_filter_for_affected_expense_groups_mixed_grouping(db):
    """
    Test construct_filter_for_affected_expense_groups with mixed grouping scenarios
    """

    workspace_id = 1
    report_id = 'rp1s1L3QtMpF'
    changed_expense_ids = [1, 2, 3]
    affected_fund_source_expense_ids = {
        FundSourceEnum.PERSONAL: [1, 2],
        FundSourceEnum.CCC: [3]
    }

    # Test case: PERSONAL report grouping, CCC expense grouping
    ExpenseGroupSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expense_group_fields': ['employee_email', 'report_id'],
            'corporate_credit_card_expense_group_fields': ['employee_email', 'expense_id']
        }
    )

    filter_query = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    assert filter_query is not None

    # Test case: PERSONAL expense grouping, CCC report grouping
    ExpenseGroupSettings.objects.filter(workspace_id=workspace_id).update(
        reimbursable_expense_group_fields=['employee_email', 'expense_id'],
        corporate_credit_card_expense_group_fields=['employee_email', 'report_id']
    )

    filter_query = construct_filter_for_affected_expense_groups(
        workspace_id=workspace_id,
        report_id=report_id,
        changed_expense_ids=changed_expense_ids,
        affected_fund_source_expense_ids=affected_fund_source_expense_ids
    )

    assert filter_query is not None


def test_handle_expense_report_change_added_to_report(db, mocker):
    """
    Test handle_expense_report_change with ADDED_TO_REPORT action
    """
    workspace = Workspace.objects.get(id=1)

    expense_data = {
        'id': 'tx1234567890',
        'org_id': workspace.fyle_org_id,
        'report_id': 'rp1234567890'
    }

    mock_delete = mocker.patch('apps.fyle.tasks._delete_expense_groups_for_report')

    handle_expense_report_change(expense_data, 'ADDED_TO_REPORT')

    mock_delete.assert_called_once()
    args = mock_delete.call_args[0]
    assert args[0] == 'rp1234567890'
    assert args[1].id == workspace.id


def test_handle_expense_report_change_ejected_from_report(db, mocker, add_expense_report_data):
    """
    Test handle_expense_report_change with EJECTED_FROM_REPORT action
    """
    workspace = Workspace.objects.get(id=1)
    expense = add_expense_report_data['expenses'][0]

    expense_data = {
        'id': expense.expense_id,
        'org_id': workspace.fyle_org_id,
        'report_id': expense.report_id
    }

    mock_handle = mocker.patch('apps.fyle.tasks._handle_expense_ejected_from_report')

    handle_expense_report_change(expense_data, 'EJECTED_FROM_REPORT')

    mock_handle.assert_called_once()


def test_delete_expense_groups_for_report_basic(db, mocker, add_expense_report_data):
    """
    Test _delete_expense_groups_for_report deletes non-exported expense groups
    """
    workspace = Workspace.objects.get(id=1)

    expense = add_expense_report_data['expenses'][0]
    report_id = expense.report_id

    mock_delete = mocker.patch('apps.fyle.tasks.delete_expense_group_and_related_data')

    _delete_expense_groups_for_report(report_id, workspace)

    assert mock_delete.called


def test_delete_expense_groups_for_report_no_expenses(db, mocker):
    """
    Test _delete_expense_groups_for_report with no expenses in database
    Case: Non-existent report_id
    """
    workspace = Workspace.objects.get(id=1)
    report_id = 'rpNonExistent123'

    _delete_expense_groups_for_report(report_id, workspace)


def test_delete_expense_groups_for_report_with_active_task_logs(db, mocker, add_expense_report_data):
    """
    Test _delete_expense_groups_for_report skips groups with active task logs
    """
    workspace = Workspace.objects.get(id=1)
    expense_group = add_expense_report_data['expense_group']

    TaskLog.objects.create(
        workspace_id=workspace.id,
        expense_group_id=expense_group.id,
        type='CREATING_BILL',
        status='IN_PROGRESS'
    )

    report_id = expense_group.expenses.first().report_id

    mock_delete = mocker.patch('apps.fyle.tasks.delete_expense_group_and_related_data')

    _delete_expense_groups_for_report(report_id, workspace)

    assert not mock_delete.called


def test_delete_expense_groups_for_report_preserves_exported(db, mocker, add_expense_report_data):
    """
    Test _delete_expense_groups_for_report preserves exported expense groups
    """
    workspace = Workspace.objects.get(id=1)

    expense_group = add_expense_report_data['expense_group']

    expense_group.exported_at = datetime.now(tz=timezone.utc)
    expense_group.save()

    report_id = expense_group.expenses.first().report_id

    mock_delete = mocker.patch('apps.fyle.tasks.delete_expense_group_and_related_data')

    _delete_expense_groups_for_report(report_id, workspace)

    assert not mock_delete.called


def test_handle_expense_ejected_from_report_removes_from_group(db, add_expense_report_data):
    """
    Test _handle_expense_ejected_from_report removes expense from group
    """
    workspace = Workspace.objects.get(id=1)

    expense_group = add_expense_report_data['expense_group']
    expenses = add_expense_report_data['expenses']

    expense_to_remove = expenses[0]

    expense_data = {
        'id': expense_to_remove.expense_id,
        'report_id': None
    }

    initial_expense_count = expense_group.expenses.count()

    _handle_expense_ejected_from_report(expense_to_remove, expense_data, workspace)

    expense_group.refresh_from_db()

    assert expense_group.expenses.count() == initial_expense_count - 1
    assert expense_to_remove not in expense_group.expenses.all()
    assert ExpenseGroup.objects.filter(id=expense_group.id).exists()


def test_handle_expense_ejected_from_report_deletes_empty_group(db, add_expense_report_data):
    """
    Test _handle_expense_ejected_from_report deletes group when last expense is removed
    """
    workspace = Workspace.objects.get(id=1)

    expense_group = add_expense_report_data['expense_group']
    expense = add_expense_report_data['expenses'][0]
    expense_group.expenses.set([expense])

    expense_data = {
        'id': expense.expense_id,
        'report_id': None
    }

    group_id = expense_group.id

    _handle_expense_ejected_from_report(expense, expense_data, workspace)

    assert not ExpenseGroup.objects.filter(id=group_id).exists()


def test_handle_expense_ejected_from_report_no_group_found(db, add_expense_report_data):
    """
    Test _handle_expense_ejected_from_report when expense has no group
    """
    workspace = Workspace.objects.get(id=1)
    expense = add_expense_report_data['expenses'][0]

    # Remove expense from its group to simulate orphaned expense
    expense_group = add_expense_report_data['expense_group']
    expense_group.expenses.remove(expense)

    expense_data = {
        'id': expense.expense_id,
        'report_id': None
    }

    _handle_expense_ejected_from_report(expense, expense_data, workspace)


def test_handle_expense_ejected_from_report_with_active_task_log(db, add_expense_report_data):
    """
    Test _handle_expense_ejected_from_report skips removal when task log is active
    """
    workspace = Workspace.objects.get(id=1)

    expense_group = add_expense_report_data['expense_group']
    expense = add_expense_report_data['expenses'][0]
    initial_count = expense_group.expenses.count()

    TaskLog.objects.create(
        workspace_id=workspace.id,
        expense_group_id=expense_group.id,
        type='CREATING_BILL',
        status='ENQUEUED'
    )

    expense_data = {
        'id': expense.expense_id,
        'report_id': None
    }

    _handle_expense_ejected_from_report(expense, expense_data, workspace)

    expense_group.refresh_from_db()

    assert expense_group.expenses.count() == initial_count
    assert expense in expense_group.expenses.all()


def test_handle_expense_report_change_ejected_expense_not_found(db, mocker):
    """
    Test handle_expense_report_change when expense doesn't exist in workspace (EJECTED_FROM_REPORT)
    """
    workspace = Workspace.objects.get(id=1)

    expense_data = {
        'id': 'txNonExistent999',
        'org_id': workspace.fyle_org_id,
        'report_id': None
    }

    handle_expense_report_change(expense_data, 'EJECTED_FROM_REPORT')


def test_handle_expense_report_change_ejected_from_exported_group(db, add_expense_report_data):
    """
    Test handle_expense_report_change skips when expense is part of exported group (EJECTED_FROM_REPORT)
    """
    workspace = Workspace.objects.get(id=1)
    expense_group = add_expense_report_data['expense_group']
    expense = add_expense_report_data['expenses'][0]

    expense_group.exported_at = datetime.now(tz=timezone.utc)
    expense_group.save()

    expense_data = {
        'id': expense.expense_id,
        'org_id': workspace.fyle_org_id,
        'report_id': None
    }

    handle_expense_report_change(expense_data, 'EJECTED_FROM_REPORT')

    expense_group.refresh_from_db()
    assert expense in expense_group.expenses.all()


def test_handle_category_changes_for_expense(db, add_category_test_expense, add_category_test_expense_group, add_category_mapping_error, add_category_expense_attribute):
    workspace = Workspace.objects.get(id=1)
    expense = add_category_test_expense
    expense_group = add_category_test_expense_group
    error = add_category_mapping_error

    error.mapping_error_expense_group_ids = [expense_group.id, 999]
    error.save()

    handle_category_changes_for_expense(expense=expense, new_category='New Category')

    error.refresh_from_db()
    assert expense_group.id not in error.mapping_error_expense_group_ids
    assert 999 in error.mapping_error_expense_group_ids

    error.mapping_error_expense_group_ids = [expense_group.id]
    error.save()

    handle_category_changes_for_expense(expense=expense, new_category='Another Category')

    assert not Error.objects.filter(id=error.id, workspace_id=workspace.id, type='CATEGORY_MAPPING').exists()

    expense_group.delete()

    expense_group_2 = ExpenseGroup.objects.create(
        workspace_id=workspace.id,
        fund_source='PERSONAL',
        description={'employee_email': expense.employee_email},
        employee_name=expense.employee_name
    )
    expense_group_2.expenses.add(expense)

    category_attribute = add_category_expense_attribute
    category_attribute.pk = None
    category_attribute.id = None
    category_attribute.value = 'Test Category With Error'
    category_attribute.source_id = 'catErr123'
    category_attribute.save()

    existing_error = Error.objects.create(
        workspace_id=workspace.id,
        type='CATEGORY_MAPPING',
        is_resolved=False,
        expense_attribute=category_attribute,
        mapping_error_expense_group_ids=[888]
    )

    handle_category_changes_for_expense(expense=expense, new_category='Test Category With Error')

    existing_error.refresh_from_db()
    assert expense_group_2.id in existing_error.mapping_error_expense_group_ids
    assert 888 in existing_error.mapping_error_expense_group_ids

    expense_group_2.delete()

    expense_group_3 = ExpenseGroup.objects.create(
        workspace_id=workspace.id,
        fund_source='PERSONAL',
        description={'employee_email': expense.employee_email},
        employee_name=expense.employee_name
    )
    expense_group_3.expenses.add(expense)

    category_attribute_2 = add_category_expense_attribute
    category_attribute_2.pk = None
    category_attribute_2.id = None
    category_attribute_2.value = 'Unmapped Category'
    category_attribute_2.source_id = 'catUnmapped456'
    category_attribute_2.save()

    handle_category_changes_for_expense(expense=expense, new_category='Unmapped Category')

    new_error = Error.objects.filter(
        workspace_id=workspace.id,
        type='CATEGORY_MAPPING',
        expense_attribute=category_attribute_2
    ).first()

    assert new_error is not None
    assert expense_group_3.id in new_error.mapping_error_expense_group_ids
    assert new_error.error_title == 'Unmapped Category'
    assert new_error.error_detail == 'Category mapping is missing'


def test_update_non_exported_expenses_category_change(mocker, db):
    expense_data = data['raw_expense'].copy()
    expense_data['category']['name'] = 'New Category'
    expense_data['category']['sub_category'] = 'New Sub Category'
    org_id = expense_data['org_id']

    default_raw_expense = data['default_raw_expense'].copy()
    default_raw_expense['category'] = 'Old Category'
    default_raw_expense['sub_category'] = 'Old Sub Category'

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

    mock_fyle_expenses = mocker.patch('apps.fyle.tasks.FyleExpenses')
    constructed_expense = expense_data.copy()
    constructed_expense['category'] = expense_data['category']['name']
    constructed_expense['sub_category'] = expense_data['category']['sub_category']
    constructed_expense['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    mock_fyle_expenses.return_value.construct_expense_object.return_value = [constructed_expense]

    mocker.patch('apps.fyle.tasks.Expense.create_expense_objects', return_value=None)

    mock_handle_category_changes = mocker.patch(
        'apps.fyle.tasks.handle_category_changes_for_expense',
        return_value=None
    )

    update_non_exported_expenses(expense_data)

    assert mock_handle_category_changes.call_count == 1
    _, kwargs = mock_handle_category_changes.call_args
    assert kwargs['expense'] == expense_created
    assert kwargs['new_category'] == 'New Category / New Sub Category'

    expense_created.category = 'Same Category'
    expense_created.sub_category = 'Same Category'
    expense_created.save()

    expense_data_2 = data['raw_expense'].copy()
    expense_data_2['category']['name'] = 'Changed'
    expense_data_2['category']['sub_category'] = 'Changed'

    constructed_expense_2 = expense_data_2.copy()
    constructed_expense_2['category'] = 'Changed'
    constructed_expense_2['sub_category'] = 'Changed'
    constructed_expense_2['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    mock_fyle_expenses.return_value.construct_expense_object.return_value = [constructed_expense_2]

    update_non_exported_expenses(expense_data_2)

    assert mock_handle_category_changes.call_count == 2
    _, kwargs = mock_handle_category_changes.call_args
    assert kwargs['new_category'] == 'Changed'

    expense_created.category = 'Old Cat'
    expense_created.sub_category = None
    expense_created.save()

    expense_data_3 = data['raw_expense'].copy()
    expense_data_3['category']['name'] = 'New Cat'
    expense_data_3['category']['sub_category'] = None

    constructed_expense_3 = expense_data_3.copy()
    constructed_expense_3['category'] = 'New Cat'
    constructed_expense_3['sub_category'] = None
    constructed_expense_3['source_account_type'] = 'PERSONAL_CASH_ACCOUNT'
    mock_fyle_expenses.return_value.construct_expense_object.return_value = [constructed_expense_3]

    update_non_exported_expenses(expense_data_3)

    assert mock_handle_category_changes.call_count == 3
    _, kwargs = mock_handle_category_changes.call_args
    assert kwargs['new_category'] == 'New Cat'


def test_handle_org_setting_updated(db):
    """
    Test handle_org_setting_updated stores regional_settings in org_settings field
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    workspace.org_settings = {}
    workspace.save()

    handle_org_setting_updated(
        workspace_id=workspace_id,
        org_settings=data['org_settings']['org_settings_payload']
    )

    workspace.refresh_from_db()

    assert workspace.org_settings == data['org_settings']['expected_org_settings']
    assert 'other_setting' not in workspace.org_settings


def test_handle_org_setting_updated_empty_regional_settings(db):
    """
    Test handle_org_setting_updated when regional_settings is empty or missing
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    handle_org_setting_updated(
        workspace_id=workspace_id,
        org_settings=data['org_settings']['org_settings_payload_without_regional']
    )

    workspace.refresh_from_db()
    assert workspace.org_settings == data['org_settings']['expected_org_settings_empty']


def test_handle_org_setting_updated_overwrites_existing(db):
    """
    Test handle_org_setting_updated overwrites existing org_settings
    """
    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)

    workspace.org_settings = data['org_settings']['expected_org_settings']
    workspace.save()

    handle_org_setting_updated(
        workspace_id=workspace_id,
        org_settings=data['org_settings']['org_settings_payload_updated']
    )

    workspace.refresh_from_db()
    assert workspace.org_settings == data['org_settings']['expected_org_settings_updated']
