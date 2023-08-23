import json
from unittest import mock
from apps.tasks.models import TaskLog
from apps.workspaces.models import XeroCredentials, Workspace
from apps.fyle.models import Reimbursement
from .fixtures import data
from ..test_fyle.fixtures import data as fyle_data
from xerosdk.exceptions import InvalidGrant, InvalidTokenError, UnsuccessfulAuthentication 
from fyle_accounting_mappings.models import MappingSetting

def test_get_token_health(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/token_health/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    with mock.patch('apps.xero.utils.XeroConnector.__init__') as mock_call:
        mock_call.side_effect = InvalidGrant(msg='Invalid grant')
        response = api_client.get(url)
        assert response.status_code == 400

    with mock.patch('apps.xero.utils.XeroConnector.__init__') as mock_call:
        mock_call.side_effect = UnsuccessfulAuthentication(msg='Auth error')
        response = api_client.get(url)
        assert response.status_code == 400


def test_get_tenant_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/tenants/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 1


def test_post_tenant_view(mocker, api_client, test_connection):
    mocker.patch(
        'xerosdk.apis.Tenants.get_all',
        return_value = []
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/tenants/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 0
     
    xero_credential = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response['message'] == 'Xero credentials not found in workspace'


def test_get_xero_fields_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/xero_fields/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 2


def test_post_sync_dimensions(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_dimensions',
        return_value=None
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/sync_dimensions/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    workspace = Workspace.objects.get(id=workspace_id)
    destination_synced_at = workspace.destination_synced_at

    response = api_client.post(url)
    assert response.status_code == 200

    workspace.destination_synced_at = destination_synced_at
    workspace.save()

    xero_credential = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response['message'] == 'Xero credentials not found in workspace'


def test_post_refresh_dimensions(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_dimensions',
        return_value=None
    )
    mocker.patch(
        'apps.mappings.signals.upload_attributes_to_fyle',
        return_value = []
    )
    workspace_id = 1

    MappingSetting.objects.update_or_create(
            workspace_id=workspace_id,
            source_field = 'PROJECT',
            defaults={
                'destination_field': 'CUSTOMER',
                'import_to_fyle': True

            }
    )

    MappingSetting.objects.update_or_create(
            workspace_id=workspace_id,
            source_field = 'COST_CENTER',
            defaults={
                'destination_field': 'ACCOUNT',
                'import_to_fyle': True

            }
    )

    MappingSetting.objects.update_or_create(
            workspace_id = workspace_id,
            source_field = 'Ashutosh Field',
            defaults={
                'destination_field': 'CLASS',
                'import_to_fyle': True,
                'is_custom': True
            }
    )

    access_token = test_connection.access_token 
    url = '/api/workspaces/{}/xero/refresh_dimensions/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    xero_credential = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response['message'] == 'Xero credentials not found in workspace'


def test_get_destination_attributes_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/destination_attributes/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(
        url,
        data={
            'attribute_types': ['CUSTOMER'],
            'active': 'true'
        }
        )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 0
