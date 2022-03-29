from typing import Dict

from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_xero_api.utils import assert_valid

from .models import TenantMapping, GeneralMapping
from ..xero.tasks import schedule_payment_creation


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

        general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(
            workspace_id=self.__workspace_id)

        params = {
            'bank_account_name': None,
            'bank_account_id': None,
            'payment_account_name': None,
            'payment_account_id': None,
            'default_tax_code_id': None,
            'default_tax_code_name': None
        }

        if general_settings.corporate_credit_card_expenses_object == 'BANK TRANSACTION':
            assert_valid('bank_account_name' in general_mapping and general_mapping['bank_account_name'],
                         'bank account name field is blank')
            assert_valid('bank_account_id' in general_mapping and general_mapping['bank_account_id'],
                         'bank account id field is blank')

            params['bank_account_name'] = general_mapping.get('bank_account_name')
            params['bank_account_id'] = general_mapping.get('bank_account_id')

        if general_settings.sync_fyle_to_xero_payments:
            assert_valid('payment_account_name' in general_mapping and general_mapping['payment_account_name'],
                         'payment account name field is blank')
            assert_valid('payment_account_id' in general_mapping and general_mapping['payment_account_id'],
                         'payment account id field is blank')

            params['payment_account_name'] = general_mapping.get('payment_account_name')
            params['payment_account_id'] = general_mapping.get('payment_account_id')

        if general_settings.import_tax_codes:
            assert_valid('default_tax_code_name' in general_mapping and general_mapping['default_tax_code_name'],
                        'default tax code name is blank')
            assert_valid('default_tax_code_name' in general_mapping and general_mapping['default_tax_code_name'],
                        'default tax code name is blank')

            params['default_tax_code_id'] = general_mapping['default_tax_code_id'],
            params['default_tax_code_name'] = general_mapping['default_tax_code_name'],

        general_mapping_object, _ = GeneralMapping.objects.update_or_create(
            workspace_id=self.__workspace_id,
            defaults=params
        )

        schedule_payment_creation(
            sync_fyle_to_xero_payments=general_settings.sync_fyle_to_xero_payments,
            workspace_id=self.__workspace_id
        )

        return general_mapping_object
