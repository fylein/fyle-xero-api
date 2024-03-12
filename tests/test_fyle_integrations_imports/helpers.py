from fyle_integrations_imports.modules.base import Base
from fyle_integrations_platform_connector import PlatformConnector
from apps.workspaces.models import FyleCredential, XeroCredentials
from apps.xero.utils import XeroConnector
from typing import List


def get_base_class_instance(
        workspace_id: int = 1,
        source_field: str = 'PROJECT',
        destination_field: str = 'PROJECT',
        platform_class_name: str = 'projects',
        sync_after: str = None,
        destination_sync_methods: List[str] = ['customers']
):

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    base = Base(
        workspace_id = workspace_id,
        source_field = source_field,
        destination_field = destination_field,
        platform_class_name = platform_class_name,
        sync_after = sync_after,
        sdk_connection = xero_connection,
        destination_sync_methods = destination_sync_methods
    )

    return base


def get_platform_connection(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials=fyle_credentials)

    return platform
