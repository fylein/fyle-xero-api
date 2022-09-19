import json
from apps.workspaces.models import Workspace,WorkspaceGeneralSettings
from .fixtures import data
from tests.helper import dict_compare_keys


def test_export_settings(api_client, test_connection):

    workspace = Workspace.objects.get(id=1)
    workspace.onboarding_state = 'EXPORT_SETTINGS'
    workspace.save()

    workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=1).first() 
    workspace_general_settings_instance.map_merchant_to_contact = True
    workspace_general_settings_instance.save()

    url = '/api/v2/workspaces/1/export_settings/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(
        url,
        data=data['export_settings'],
        format='json'
    )

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['export_settings_response']) == [], 'workspaces api returns a diff in the keys'

    response = api_client.put(
        url,
        data=data['export_settings_missing_values'],
        format='json'
    )

    assert response.status_code == 400
