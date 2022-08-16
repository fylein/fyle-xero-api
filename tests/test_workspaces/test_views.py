import json
from apps.mappings.models import TenantMapping
from fyle_xero_api import settings
from tests.helper import dict_compare_keys
from apps.workspaces.models import Workspace, WorkspaceSchedule, WorkspaceGeneralSettings
from .fixtures import data


def test_ready_view(api_client, test_connection):

    url = '/api/workspaces/ready/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    response['message'] == 'Ready'


def test_get_workspace(api_client, test_connection):
    url = '/api/workspaces/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response == []


def test_get_workspace_by_id(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'

    workspace_id = 5

    url = '/api/workspaces/{}/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 400


def test_post_of_workspace(api_client, test_connection):

    url = '/api/workspaces/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    print(response)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


def test_connect_fyle_view(api_client, test_connection):
    workspace_id = 1
    
    url = '/api/workspaces/{}/credentials/fyle/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 200
    
    url = '/api/workspaces/{}/credentials/fyle/delete/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.delete(url)
    assert response.status_code == 200

    url = '/api/workspaces/{}/credentials/fyle/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 400

    code = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiJ0cGFWVVhtd2FZWGVRIiwicmVzcG9uc2VfdHlwZSI6ImNvZGUiLCJjbHVzdGVyX2RvbWFpbiI6Imh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2giLCJvcmdfdXNlcl9pZCI6Im91NDV2ekhFWUJGUyIsImV4cCI6MTY1MjI2MzMwMH0.D6WdXnkUcKMU98VjZEMz6OH1kGtRXVj1uLGsTeIo0IQ'
    url = '/api/workspaces/{}/connect_fyle/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(
        url,
        data={'code': code}    
    )
    assert response.status_code == 500


def test_connect_xero_view(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/credentials/xero/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    print(response)

    url = '/api/workspaces/{}/credentials/xero/delete/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.delete(url)
    assert response.status_code == 200

    url = '/api/workspaces/{}/credentials/xero/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 400

    code = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiJ0cGFWVVhtd2FZWGVRIiwicmVzcG9uc2VfdHlwZSI6ImNvZGUiLCJjbHVzdGVyX2RvbWFpbiI6Imh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2giLCJvcmdfdXNlcl9pZCI6Im91NDV2ekhFWUJGUyIsImV4cCI6MTY1MjI2MzMwMH0.D6WdXnkUcKMU98VjZEMz6OH1kGtRXVj1uLGsTeIo0IQ'
    url = '/api/workspaces/{}/connect_xero/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(
        url,
        data={'code': code}    
    )

    response = api_client.post(url)
    print(response)
    assert response.status_code == 500


def test_revoke_xero_connection(api_client, test_connection):
    workspace_id = 1
    
    url = '/api/workspaces/{}/connection/xero/revoke/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.connection_id = 'sdfghjkl'

    response = api_client.post(url)
    assert response.status_code == 200


def test_workspace_schedule(api_client, test_connection):
    workspace_id = 3

    url = '/api/workspaces/{}/schedule/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)

    WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )
    response = api_client.get(url)

    response = json.loads(response.content)
    print(response)
    # assert response == {'id': 2, 'enabled': False, 'start_datetime': None, 'interval_hours': None, 'workspace': 2, 'schedule': None}

    response = api_client.post(
        url,
        data={
            'schedule_enabled': True,
            'hours': 1}    
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    print(response)
    assert response == {'id': 2, 'enabled': True, 'start_datetime': None, 'interval_hours': 1, 'workspace': 2, 'schedule': None}


def test_get_general_settings_detail(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/settings/general/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace_general_settings_payload']) == [], 'general_setting api returns a diff in keys'

    response = api_client.post(
        url,
        data=data['workspace_general_settings_payload'],
        format='json'
    )

    assert response.status_code==200

    response = api_client.patch(
        url,
        data = {
            'sync_fyle_to_xero_payments': False
        }
    )
    assert response.status_code == 200

    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_setting.delete()

    response = api_client.get(url)
    assert response.status_code == 400


def test_xero_external_signup_view(api_client, test_connection):
    url = '/api/workspaces/external_signup/'
    code = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiJ0cGFWVVhtd2FZWGVRIiwicmVzcG9uc2VfdHlwZSI6ImNvZGUiLCJjbHVzdGVyX2RvbWFpbiI6Imh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2giLCJvcmdfdXNlcl9pZCI6Im91NDV2ekhFWUJGUyIsImV4cCI6MTY1MjI2MzMwMH0.D6WdXnkUcKMU98VjZEMz6OH1kGtRXVj1uLGsTeIo0IQ'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(
        url,
        data = {
            'code': code,
            'redirect_uri': settings.XERO_REDIRECT_URI
        })
    assert response.status_code == 500
