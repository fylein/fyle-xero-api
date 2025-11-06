import pytest
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, MappingSetting

from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, XeroCredentials


@pytest.fixture
def create_mapping_setting(db):
    workspace_id = 1

    MappingSetting.objects.update_or_create(
        source_field="COST_CENTER",
        workspace_id=workspace_id,
        destination_field="COST_CENTER",
        defaults={"import_to_fyle": True, "is_custom": False},
    )

    DestinationAttribute.bulk_create_or_update_destination_attributes(
        [
            {
                "attribute_type": "COST_CENTER",
                "display_name": "Cost center",
                "value": "sample",
                "destination_id": "7b354c1c-cf59-42fc-9449-a65c51988335",
            }
        ],
        "COST_CENTER",
        1,
        True,
    )


@pytest.fixture
def create_temp_workspace(db):
    workspace_id = 3
    workspace = Workspace.objects.create(
        id=workspace_id,
        name="Fyle for Hrishabh Testing",
        fyle_org_id="Testing123",
        xero_short_code="xero123",
        last_synced_at=None,
        source_synced_at=None,
        destination_synced_at=None,
        xero_accounts_last_synced_at=None
    )
    LastExportDetail.objects.create(workspace=workspace)


@pytest.fixture
def add_xero_credentials(db, create_temp_workspace):
    workspace_id = 3
    XeroCredentials.objects.create(
        workspace_id=workspace_id,
        refresh_token="refresh_token",
        is_expired=False,
    )


@pytest.fixture()
def add_fyle_credentials(db):
    workspace_id = 3

    FyleCredential.objects.create(
        refresh_token="refresh_token",
        workspace_id=workspace_id,
        cluster_domain="https://staging.fyle.tech",
    )


@pytest.fixture
def add_corporate_card_attributes(db):
    """
    Create corporate card and category expense attributes along with their destination attributes
    for testing card mapping signals
    """
    workspace_id = 1

    # Create expense attributes
    corporate_card = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CORPORATE_CARD',
        display_name='Corporate Card',
        value='Test Card',
        source_id='card_test_123',
        active=True
    )

    category = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        display_name='Category',
        value='Test Category',
        source_id='cat_test_456',
        active=True
    )

    # Create destination attributes
    bank_account = DestinationAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='BANK_ACCOUNT',
        display_name='Bank Account',
        value='Test Bank',
        destination_id='bank_123',
        active=True
    )

    account = DestinationAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='ACCOUNT',
        display_name='Account',
        value='Test Account',
        destination_id='acc_456',
        active=True
    )

    return {
        'corporate_card': corporate_card,
        'category': category,
        'bank_account': bank_account,
        'account': account
    }
