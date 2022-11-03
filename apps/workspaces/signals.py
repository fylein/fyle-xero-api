from apps.workspaces.models import Workspace
from fyle_accounting_mappings.models import DestinationAttribute, Mapping
from apps.mappings.models import TenantMapping

def post_delete_xero_connection(workspace_id):
    """
    Post delete qbo connection
    :return: None
    """
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.onboarding_state in ('CONNECTION', 'EXPORT_SETTINGS'):
        tenant_mapping = TenantMapping.objects.filter(workspace_id=workspace_id).first()
        tenant_mapping.tenant_name = None
        tenant_mapping.tenant_id = None
        tenant_mapping.connection_id = None
        tenant_mapping.save()

        Mapping.objects.filter(workspace_id=workspace_id, source_type='EMPLOYEE').delete()
        DestinationAttribute.objects.filter(workspace_id=workspace_id).delete()
        workspace.onboarding_state = 'CONNECTION'
        workspace.xero_short_code = None
        workspace.xero_currency = None
        workspace.save()
