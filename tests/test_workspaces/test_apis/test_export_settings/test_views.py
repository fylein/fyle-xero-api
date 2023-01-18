import json
from apps.fyle.models import ExpenseGroupSettings
from apps.workspaces.models import Workspace,WorkspaceGeneralSettings
from .fixtures import data
from tests.helper import dict_compare_keys


def test_export_settings(api_client, test_connection):

    workspace_id = 1

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.onboarding_state = 'EXPORT_SETTINGS'
    workspace.save()

    workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=1).first() 
    workspace_general_settings_instance.map_merchant_to_contact = True
    workspace_general_settings_instance.save()

    expense_group_settings_instance = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings_instance.ccc_export_date_type = ''
    expense_group_settings_instance.expense_state = ''
    expense_group_settings_instance.save()

    url = '/api/v2/workspaces/{}/export_settings/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.put(
        url,
        data=data['export_settings'],
        format='json'
    )

    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['export_settings_response']) == [], 'Export settings api returns a diff in the keys'

    response = api_client.put(
        url,
        data=data['export_settings_missing_values'],
        format='json'
    )

    assert response.status_code == 400
