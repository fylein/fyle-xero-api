from datetime import datetime, timezone

from django_q.tasks import Chain
from fyle_accounting_mappings.models import MappingSetting

from apps.fyle.enums import FyleAttributeEnum
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.utils import XeroConnector
from apps.mappings.helpers import is_auto_sync_allowed
from apps.mappings.constants import SYNC_METHODS


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
    xero_credentials = XeroCredentials.get_active_xero_credentials(
        workspace_id=workspace_id
    )
    xero_connector = get_xero_connector(workspace_id=workspace_id)

    mapping_settings = MappingSetting.objects.filter(
        workspace_id=workspace_id, import_to_fyle=True
    )
    workspace_general_settings: WorkspaceGeneralSettings = (
        WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    )
    chain = Chain()

    ALLOWED_SOURCE_FIELDS = [
        FyleAttributeEnum.PROJECT,
        FyleAttributeEnum.COST_CENTER,
    ]

    for mapping_setting in mapping_settings:
        if mapping_setting.source_field in ALLOWED_SOURCE_FIELDS:
            # run new_schedule_or_delete_fyle_import_tasks
            chain.append(
                'fyle_integrations_imports.tasks.trigger_import_via_schedule',
                workspace_id,
                mapping_setting.destination_field,
                mapping_setting.source_field,
                'apps.xero.utils.XeroConnector',
                xero_credentials,
                [SYNC_METHODS.get(mapping_setting.destination_field.upper(), 'tracking_categories')],
                is_auto_sync_allowed(workspace_general_settings, mapping_setting),
                False,
                None,
                mapping_setting.is_custom,
                q_options={
                    'cluster': 'import'
                }
            )

        elif mapping_setting.is_custom:
            # run async_auto_create_custom_field_mappings
            chain.append(
                "apps.mappings.tasks.async_auto_create_custom_field_mappings",
                int(workspace_id),
                q_options={
                    'cluster': 'import'
                }
            )
        elif workspace_general_settings.import_suppliers_as_merchants:
            # run auto_create_suppliers_as_merchant
            chain.append(
                "apps.mappings.tasks.auto_create_suppliers_as_merchants", workspace_id,
                q_options={
                    'cluster': 'import'
                }
            )

    if chain.length() > 0:
        chain.run()

    xero_connector.sync_dimensions(workspace_id)

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.destination_synced_at = datetime.now()
    workspace.save(update_fields=["destination_synced_at"])
