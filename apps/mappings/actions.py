import logging

from xerosdk.exceptions import UnsuccessfulAuthentication

from apps.mappings.models import TenantMapping
from apps.mappings.utils import MappingUtils
from apps.workspaces.models import Workspace, XeroCredentials
from apps.xero.utils import XeroConnector

logger = logging.getLogger(__name__)


def create_tenant_mapping(workspace_id, tenant_mapping_payload):
    mapping_utils = MappingUtils(workspace_id)
    tenant_mapping_object = mapping_utils.create_or_update_tenant_mapping(
        tenant_mapping_payload
    )
    xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace_id).first()
    workspace = Workspace.objects.filter(id=workspace_id).first()

    try:
        xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)
        tenant_mapping = TenantMapping.objects.filter(workspace_id=workspace_id).first()
        company_info = xero_connector.get_organisations()[0]
        workspace.xero_currency = company_info['BaseCurrency']
        workspace.save()
        xero_credentials.country = company_info['CountryCode']
        xero_credentials.save()

        if tenant_mapping and not tenant_mapping.connection_id:
            connections = xero_connector.connection.connections.get_all()
            connection = list(
                filter(
                    lambda connection: connection['tenantId']
                    == tenant_mapping.tenant_id,
                    connections,
                )
            )

            if connection:
                tenant_mapping.connection_id = connection[0]['id']
                tenant_mapping.save()

            if workspace.onboarding_state == 'TENANT_MAPPING':
                workspace.onboarding_state = 'EXPORT_SETTINGS'
                workspace.save()

    except UnsuccessfulAuthentication:
        logger.info('Xero refresh token is invalid for workspace_id - %s', workspace_id)

    except Exception:
        logger.info('Error while fetching company information')

    return tenant_mapping_object
