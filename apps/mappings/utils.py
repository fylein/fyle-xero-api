from typing import Dict

from django.db.models import Q
from fyle_accounting_mappings.models import MappingSetting

from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_xero_api.utils import assert_valid

from .models import TenantMapping, GeneralMapping


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

    def create_or_update_general_mapping(self, general_mapping: Dict):
        """
        Create or update General mappings
        :param general_mapping: general mapping payload
        :return: general mappings objects
        """

        general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=self.__workspace_id)

        params = {
            'bank_account_name': None,
            'bank_account_id': None,
        }

        if general_settings.corporate_credit_card_expenses_object == 'BANK TRANSACTION':
            assert_valid('bank_account_name' in general_mapping and general_mapping['bank_account_name'],
                         'bank account name field is blank')
            assert_valid('bank_account_id' in general_mapping and general_mapping['bank_account_id'],
                         'bank account id field is blank')

            params['bank_account_name'] = general_mapping.get('bank_account_name')
            params['bank_account_id'] = general_mapping.get('bank_account_id')

        general_mapping_object, _ = GeneralMapping.objects.update_or_create(
            workspace_id=self.__workspace_id,
            defaults=params
        )

        return general_mapping_object
