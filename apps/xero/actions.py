from apps.workspaces.models import XeroCredentials, Workspace
from .utils import XeroConnector

from datetime import datetime, timezone
from apps.workspaces.models import XeroCredentials, Workspace, WorkspaceGeneralSettings
from django_q.tasks import Chain

from fyle_accounting_mappings.models import MappingSetting

def get_xero_connector(workspace_id):
    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
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
        workspace.save(update_fields=['destination_synced_at'])


def refersh_xero_dimension(workspace_id):
    workspace_id = workspace_id
    xero_connector = get_xero_connector(workspace_id=workspace_id)

    mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id, import_to_fyle=True)
    workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    chain = Chain()

    for mapping_setting in mapping_settings:
        if mapping_setting.source_field == 'PROJECT':
            # run auto_import_and_map_fyle_fields
            chain.append('apps.mappings.queue.auto_import_and_map_fyle_fields', int(workspace_id))
        elif mapping_setting.source_field == 'COST_CENTER':
            # run auto_create_cost_center_mappings
            chain.append('apps.mappings.tasks.auto_create_cost_center_mappings', int(workspace_id))
        elif mapping_setting.is_custom:
            # run async_auto_create_custom_field_mappings
            chain.append('apps.mappings.tasks.async_auto_create_custom_field_mappings', int(workspace_id))
        elif workspace_general_settings.import_suppliers_as_merchants:
            # run auto_create_suppliers_as_merchant
            chain.append('apps.mappings.tasks.auto_create_suppliers_as_merchants', workspace_id)
    
    if chain.length() > 0:
        chain.run()

    xero_connector.sync_dimensions(workspace_id)

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.destination_synced_at = datetime.now()
    workspace.save(update_fields=['destination_synced_at'])
