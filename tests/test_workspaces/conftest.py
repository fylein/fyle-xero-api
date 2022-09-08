import pytest
from fyle_xero_api import settings
from apps.workspaces.models import Workspace, XeroCredentials, FyleCredential
from datetime import datetime,timezone

@pytest.fixture
def add_workspace_to_database():
    """
    Add worksapce to database fixture
    """
    workspace = Workspace.objects.create(
        id=100,
        name = 'Fyle for labhvam2',
        fyle_org_id = 'l@bhv@m2',
        xero_short_code = '',
        last_synced_at = None,
        source_synced_at = None,
        destination_synced_at = None,
        xero_accounts_last_synced_at = datetime.now(tz=timezone.utc),
        created_at = datetime.now(tz=timezone.utc),
        updated_at = datetime.now(tz=timezone.utc)
    )

    workspace.save()


@pytest.fixture()
def add_xero_credentials(db):
    workspace_id = 2

    XeroCredentials.objects.create(
        refresh_token = '',
        workspace_id = workspace_id
    )


@pytest.fixture()
def add_fyle_credentials(db):
    workspace_id = 2

    FyleCredential.objects.create(
        refresh_token=settings.FYLE_REFRESH_TOKEN,
        workspace_id=workspace_id,
        cluster_domain='https://staging.fyle.tech'
    )
