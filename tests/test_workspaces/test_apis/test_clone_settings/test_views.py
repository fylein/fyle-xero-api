import json
from apps.workspaces.models import Workspace,WorkspaceGeneralSettings
from .fixtures import data
from tests.helper import dict_compare_keys


def assert_4xx_cases(api_client, url, data):
    response = api_client.put(
        url,
        data=data,
        format='json'
    )

    assert response.status_code == 400

    assert 'This field is required.' in str(response.data), 'clone settings api returns a diff in the message'


def test_clone_settings(api_client, test_connection):
    workspace = Workspace.objects.get(id=1)
    workspace.onboarding_state = 'COMPLETE'
    workspace.save()

    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.patch(
        url,
        data=data['clone_settings'],
        format='json'
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert dict_compare_keys(response, data['clone_settings_response']) == [], 'clone settings api returns a diff in the keys'

    response = api_client.patch(
        url,
        data=data['clone_settings_missing_values'],
        format='json'
    )

    assert response.status_code == 400

def test_4xx_export_settings(api_client, test_connection):
    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    assert_4xx_cases(api_client, url, {})

def test_4xx_import_settings(api_client, test_connection):
    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    assert_4xx_cases(api_client, url, {
        'export_settings': data['clone_settings']['export_settings']
    })

def test_4xx_advanced_settings(api_client, test_connection):
    url = '/api/v2/workspaces/1/clone_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    assert_4xx_cases(api_client, url, {
        'export_settings': data['clone_settings']['export_settings'],
        'import_settings': data['clone_settings']['import_settings']
    })

def test_clone_settings_exists(api_client, test_connection):
    workspace = Workspace.objects.get(id=1)
    workspace.onboarding_state = 'COMPLETE'
    workspace.save()

    url = '/api/user/clone_settings/exists/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.get(
        url,
        data=data['clone_settings_exists'],
        format='json'
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert dict_compare_keys(response, data['clone_settings_exists']) == [], 'clone settings api returns a diff in the keys'

    Workspace.objects.update(onboarding_state='EXPORT_SETTINGS')

    response = api_client.get(
        url,
        data=data['clone_settings_exists'],
        format='json'
    )

    assert response.status_code == 200
    response = json.loads(response.content)
    assert dict_compare_keys(response, data['clone_settings_not_exists']) == [], 'clone settings api returns a diff in the keys'
