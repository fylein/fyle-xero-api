from datetime import datetime, timezone

from apps.mappings.queue import construct_tasks_and_chain_import_fields_to_fyle

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.utils import XeroConnector


def get_xero_connector(workspace_id):
    xero_credentials = XeroCredentials.get_active_xero_credentials(
        workspace_id=workspace_id
    )
    return XeroConnector(xero_credentials, workspace_id=workspace_id)


def sync_tenant(workspace_id):
    xero_connector = get_xero_connector(workspace_id=workspace_id)
    tenants = xero_connector.sync_tenants()
    return tenants


def sync_dimensions(workspace_id):
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.destination_synced_at:
        time_interval = datetime.now(timezone.utc) - workspace.destination_synced_at

    if workspace.destination_synced_at is None or time_interval.days > 0:
        xero_connector = get_xero_connector(workspace_id=workspace_id)

        xero_connector.sync_dimensions(workspace_id)

        workspace.destination_synced_at = datetime.now()
        workspace.save(update_fields=["destination_synced_at"])


def refersh_xero_dimension(workspace_id):
    workspace_id = workspace_id
    xero_connector = get_xero_connector(workspace_id=workspace_id)

    workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

    if workspace_general_settings:
        construct_tasks_and_chain_import_fields_to_fyle(workspace_id)

    xero_connector.sync_dimensions(workspace_id)

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.destination_synced_at = datetime.now()
    workspace.save(update_fields=["destination_synced_at"])
