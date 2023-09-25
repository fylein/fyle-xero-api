import json

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from tests.helper import dict_compare_keys
from tests.test_fyle.fixtures import data as fyle_data
from tests.test_workspaces.test_apis.test_import_settings.fixtures import data


def test_import_settings(api_client, mocker, test_connection):
    mocker.patch(
        "fyle_integrations_platform_connector.apis.ExpenseCustomFields.post",
        return_value=[],
    )

    mocker.patch(
        "fyle.platform.apis.v1beta.admin.ExpenseFields.list_all",
        return_value=fyle_data["get_all_expense_fields"],
    )
    workspace = Workspace.objects.get(id=1)
    workspace.onboarding_state = "IMPORT_SETTINGS"
    workspace.save()

    workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(
        workspace_id=1
    ).first()
    workspace_general_settings_instance.map_merchant_to_contact = True
    workspace_general_settings_instance.save()

    url = "/api/v2/workspaces/1/import_settings/"
    api_client.credentials(
        HTTP_AUTHORIZATION="Bearer {}".format(test_connection.access_token)
    )
    response = api_client.put(url, data=data["import_settings"], format="json")

    assert response.status_code == 200

    response = json.loads(response.content)
    assert (
        dict_compare_keys(response, data["import_settings_response"]) == []
    ), "Import settings api returns a diff in the keys"

    response = api_client.put(url, data=data["import_settings_2"], format="json")

    assert response.status_code == 200

    response = json.loads(response.content)
    assert (
        dict_compare_keys(response, data["import_settings_response"]) == []
    ), "Import settings api returns a diff in the keys"

    response = api_client.put(
        url, data=data["import_settings_missing_values"], format="json"
    )
    assert response.status_code == 400
