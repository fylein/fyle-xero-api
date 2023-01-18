import json
import pytest
from apps.mappings.models import GeneralMapping, TenantMapping
from apps.workspaces.models import WorkspaceGeneralSettings
from .fixtures import data
from ..test_xero.fixtures import data as xero_data


def test_tenant_mapping_view(api_client, test_connection, mocker):

    workspace_id = 1
    tenenat_mapping = TenantMapping.objects.get(workspace_id=workspace_id)

    mocker.patch(
        'xerosdk.apis.Organisations.get_all',
        return_value=xero_data['get_all_organisations']
    )

    url = '/api/workspaces/{}/mappings/tenant/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    payload = {
        'tenant_name': 'sample',
        'tenant_id': 'sdfghj'
    }

    response = api_client.post(
        url,
        data=payload
    )
    assert response.status_code == 200

    mocker.patch(
        'xerosdk.apis.Connections.get_all',
        return_value=[{'tenantId': tenenat_mapping.tenant_id, 'id': 'asdfghjk'}]
    )

    payload = {
        'tenant_name': 'Demo Company (Global)',
        'tenant_id': '36ab1910-11b3-4325-b545-8d1170668ab3'
    }

    response = api_client.post(
        url,
        data=payload
    )
    assert response.status_code == 200

    tenenat_mapping.delete()

    response = api_client.get(url)
    assert response.status_code == 400
    
    
@pytest.mark.django_db(databases=['default'])
def test_get_general_mappings(api_client, test_connection):
    '''
    Test get of general mappings
    '''
    workspace_id = 1
    url = '/api/workspaces/{}/mappings/general/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200
    response = json.loads(response.content)

    general_mapping = GeneralMapping.objects.get(workspace_id=1)
    general_mapping.default_ccc_vendor_name = ''
    general_mapping.use_employee_department = True
    general_mapping.save()
    response = api_client.get(url)

    GeneralMapping.objects.get(workspace_id=1).delete()

    response = api_client.get(url)

    assert response.status_code == 400
    assert response.data['message'] == 'General mappings do not exist for the workspace'


@pytest.mark.django_db(databases=['default'])
def test_post_general_mappings(api_client, test_connection):
    '''
    Test post of general mappings
    '''
    workspace_id = 1
    url = '/api/workspaces/{}/mappings/general/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    payload = data['general_mapping_payload']

    response = api_client.post(
        url,
        data=payload,
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response['bank_account_name'] == 'Business Bank Account'

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    general_settings.corporate_credit_card_expenses_object = 'BANK TRANSACTION'
    general_settings.sync_fyle_to_xero_payments = True
    general_settings.import_tax_codes = True
    general_settings.save()

    response = api_client.post(
        url,
        data=payload
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response['default_tax_code_id'] == 'INPUT'


def test_auto_map_employee(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/mappings/auto_map_employees/trigger/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.auto_map_employees = ''
    general_settings.save()

    response = api_client.post(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response['message'] == 'Employee mapping preference not found for this workspace'
    