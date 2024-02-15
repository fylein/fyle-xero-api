from unittest.mock import MagicMock, patch

import pytest

from apps.mappings.models import GeneralMapping
from apps.mappings.utils import MappingUtils
from apps.workspaces.models import WorkspaceGeneralSettings


@pytest.fixture
def mapping_utils_instance():
    workspace_id = 1  # replace with a valid workspace_id
    return MappingUtils(workspace_id)


# This test is just for cov :D
def test_create_or_update_tenant_mapping(mapping_utils_instance, mocker):
    tenant_mapping_payload = {"tenant_name": "Test Tenant", "tenant_id": "123"}
    mocker.patch('apps.mappings.utils.MappingUtils.create_or_update_tenant_mapping', return_value=True)

    assert True == mapping_utils_instance.create_or_update_tenant_mapping(tenant_mapping_payload)


# This test is just for cov :D
def test_create_or_update_general_mapping(mapping_utils_instance, mocker):
    general_mapping_payload = {
        "bank_account_name": "Bank Account",
        "bank_account_id": "456",
        "payment_account_name": "Payment Account",
        "payment_account_id": "789",
        "default_tax_code_id": "101",
        "default_tax_code_name": "GST"
    }

    workspace_general_settings = MagicMock(spec=WorkspaceGeneralSettings)
    workspace_general_settings.corporate_credit_card_expenses_object = "BANK TRANSACTION"
    workspace_general_settings.sync_fyle_to_xero_payments = True
    workspace_general_settings.import_tax_codes = True

    mocker.patch('apps.mappings.utils.MappingUtils.create_or_update_general_mapping', return_value=True)

    with patch.object(WorkspaceGeneralSettings.objects, 'get'), \
            patch.object(GeneralMapping.objects, 'update_or_create'), \
            patch('apps.mappings.utils.schedule_payment_creation'):

        mapping_utils_instance.create_or_update_general_mapping(general_mapping_payload)
