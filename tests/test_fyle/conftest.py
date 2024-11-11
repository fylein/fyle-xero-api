from datetime import datetime, timezone

import pytest

from apps.fyle.models import ExpenseGroupSettings
from apps.workspaces.models import Workspace


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
