import pytest
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping

from apps.mappings.models import TenantMapping
from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, XeroCredentials


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


@pytest.fixture()
def add_tenant_mapping(db, create_temp_workspace):
    workspace = Workspace.objects.filter(id = 3).first()

    tenant_mapping = TenantMapping(
        tenant_name="sample", tenant_id="wertyui", workspace=workspace
    )
    tenant_mapping.save()


@pytest.fixture
def create_project_mapping(db, create_temp_workspace):
    workspace_id = 3
    expense_attribute = ExpenseAttribute.objects.create(attribute_type='PROJECT', display_name='project', value='Concrete', source_id='src123', workspace_id=workspace_id, active=True)
    destination_attribute = DestinationAttribute.objects.create(attribute_type='CUSTOMER', display_name='customer', value='Concrete', destination_id='dest123', workspace_id=workspace_id, active=True)
    Mapping.objects.create(source_type='PROJECT', destination_type='CUSTOMER', destination_id=destination_attribute.id, source_id=expense_attribute.id, workspace_id=workspace_id)


@pytest.fixture
def create_category_mapping(db, create_temp_workspace):
    workspace_id = 3
    expense_attribute = ExpenseAttribute.objects.create(attribute_type='CATEGORY', display_name='category', value='Concrete', source_id='src123', workspace_id=workspace_id, active=True)
    destination_attribute = DestinationAttribute.objects.create(attribute_type='ACCOUNT', display_name='account', value='Concrete', destination_id='dest123', workspace_id=workspace_id, active=True)
    Mapping.objects.create(source_type='CATEGORY', destination_type='ACCOUNT', destination_id=destination_attribute.id, source_id=expense_attribute.id, workspace_id=workspace_id)
