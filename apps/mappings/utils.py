from typing import Dict

from fyle_xero_api.utils import assert_valid

from .models import TenantMapping


class MappingUtils:
    def __init__(self, workspace_id):
        self.__workspace_id = workspace_id

    def create_or_update_tenant_mapping(self, tenant_mapping: Dict):
        """
        Create or update Tenant mappings
        :param tenant_mapping: project mapping payload
        :return: tenant mappings objects
        """

        assert_valid('tenant_name' in tenant_mapping and tenant_mapping['tenant_name'],
                     'tenant name field is blank')
        assert_valid('tenant_id' in tenant_mapping and tenant_mapping['tenant_id'],
                     'tenant id field is blank')

        tenant_mapping_object, _ = TenantMapping.objects.update_or_create(
            workspace_id=self.__workspace_id,
            defaults={
                'tenant_name': tenant_mapping['tenant_name'],
                'tenant_id': tenant_mapping['tenant_id']
            }
        )

        return tenant_mapping_object
