from datetime import datetime, timezone

import pytest
from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import Error
from apps.workspaces.models import LastExportDetail, Workspace


@pytest.fixture
def create_temp_workspace(db):
    workspace = Workspace.objects.create(
        id=98,
        name="Fyle for Testing",
        fyle_org_id="Testing",
        xero_short_code="erfg",
        last_synced_at=None,
        source_synced_at=None,
        destination_synced_at=None,
        xero_accounts_last_synced_at=None,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )

    workspace.save()

    ExpenseGroupSettings.objects.create(
        reimbursable_expense_group_fields="{employee_email,report_id,claim_number,fund_source}",
        corporate_credit_card_expense_group_fields="{fund_source,employee_email,claim_number,expense_id,report_id}",
        reimbursable_expense_state="PAYMENT PROCESSING",
        ccc_expense_state="PAYMENT_PROCESSING",
        workspace_id=98,
        reimbursable_export_date_type="current_date",
        ccc_export_date_type="spent_at",
    )
    LastExportDetail.objects.create(workspace=workspace)


@pytest.fixture
def update_config_for_split_expense_grouping(db):
    def _update_config_for_split_expense_grouping(general_settings, expense_group_settings):
        general_settings.corporate_credit_card_expenses_object = 'BANK TRANSACTION'
        general_settings.save()
        expense_group_settings.split_expense_grouping = 'SINGLE_LINE_ITEM'
        expense_group_settings.corporate_credit_card_expense_group_fields = [
            'expense_id',
            'claim_number',
            'fund_source',
            'employee_email',
            'report_id',
            'spent_at',
            'report_id'
        ]
        expense_group_settings.save()
    return _update_config_for_split_expense_grouping


@pytest.fixture
def add_category_test_expense(db):
    workspace = Workspace.objects.get(id=1)
    expense = Expense.objects.create(
        workspace_id=workspace.id,
        expense_id='txCategoryTest',
        employee_email='category.test@test.com',
        employee_name='Category Test User',
        category='Test Category',
        amount=100,
        currency='USD',
        org_id=workspace.fyle_org_id,
        settlement_id='setlCat',
        report_id='rpCat',
        spent_at='2024-01-01T00:00:00Z',
        expense_created_at='2024-01-01T00:00:00Z',
        expense_updated_at='2024-01-01T00:00:00Z',
        fund_source='PERSONAL'
    )
    return expense


@pytest.fixture
def add_category_test_expense_group(db, add_category_test_expense):
    workspace = Workspace.objects.get(id=1)
    expense = add_category_test_expense
    expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace.id,
        fund_source='PERSONAL',
        description={'employee_email': expense.employee_email},
        employee_name=expense.employee_name
    )
    expense_group.expenses.add(expense)
    return expense_group


@pytest.fixture
def add_category_mapping_error(db, add_category_test_expense_group):
    workspace = Workspace.objects.get(id=1)
    expense_group = add_category_test_expense_group
    error = Error.objects.create(
        workspace_id=workspace.id,
        type='CATEGORY_MAPPING',
        is_resolved=False,
        mapping_error_expense_group_ids=[expense_group.id]
    )
    return error


@pytest.fixture
def add_category_expense_attribute(db):
    workspace = Workspace.objects.get(id=1)
    expense_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace.id,
        attribute_type='CATEGORY',
        value='Test Category Attribute',
        display_name='Category',
        source_id='catTest123'
    )
    return expense_attribute
