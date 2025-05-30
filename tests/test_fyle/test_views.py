import json

import pytest

from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, Workspace
from tests.helper import dict_compare_keys
from tests.test_fyle.fixtures import data


def test_expense_group_view(api_client, test_connection):
    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/expense_groups/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.get(
        url,
        {
            "tasklog__status": "COMPLETE",
            "exported_at_gte": "2022-08-02 20:25:00",
            "exported_at_lte": "2022-08-02 20:30:00"
        },
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response["count"] == 10

    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=1, type="FETCHING_EXPENSES", defaults={"status": "IN_PROGRESS"}
    )


def test_expense_group_settings_view(api_client, test_connection):
    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/expense_group_settings/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))
    response = api_client.get(url)
    response = json.loads(response.content)

    assert (
        dict_compare_keys(response, data["expense_group_setting_response"]) == []
    ), "expense group api return diffs in keys"
    assert response["reimbursable_expense_group_fields"] == [
        "employee_email",
        "report_id",
        "claim_number",
        "fund_source",
    ]
    assert response["ccc_expense_state"] == "PAYMENT_PROCESSING"
    assert response["reimbursable_expense_state"] == "PAYMENT_PROCESSING"
    assert response["reimbursable_export_date_type"] == "current_date"


def test_expense_fields_view(api_client, test_connection):
    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/expense_fields/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response[0] == data["expense_fields_response"][0]


@pytest.mark.django_db(databases=["default"])
def test_fyle_sync_dimension(api_client, test_connection, mocker):
    mocker.patch(
        "fyle.platform.apis.v1.admin.Employees.list_all",
        return_value=data["get_all_employees"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.Categories.list_all",
        return_value=data["get_all_categories"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.Projects.list_all",
        return_value=data["get_all_projects"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.CostCenters.list_all",
        return_value=data["get_all_cost_centers"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.ExpenseFields.list_all",
        return_value=data["get_all_expense_fields"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.CorporateCards.list_all",
        return_value=data["get_all_corporate_cards"],
    )

    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/sync_dimensions/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    workspace = Workspace.objects.get(id=1)
    workspace.source_synced_at = None
    workspace.save()

    response = api_client.post(url)
    assert response.status_code == 200


def test_fyle_sync_dimension_fail(api_client, test_connection):
    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/sync_dimensions/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    workspace = Workspace.objects.get(id=1)
    workspace.source_synced_at = None
    workspace.save()

    fyle_credentials = FyleCredential.objects.get(workspace_id=1)
    fyle_credentials.delete()

    new_response = api_client.post(url)
    assert new_response.status_code == 400
    assert new_response.data["message"] == "Fyle credentials not found in workspace"


def test_fyle_refresh_dimension(api_client, test_connection, mocker):
    mocker.patch(
        "fyle.platform.apis.v1.admin.Employees.list_all",
        return_value=data["get_all_employees"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.Categories.list_all",
        return_value=data["get_all_categories"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.Projects.list_all",
        return_value=data["get_all_projects"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.CostCenters.list_all",
        return_value=data["get_all_cost_centers"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.ExpenseFields.list_all",
        return_value=data["get_all_expense_fields"],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.CorporateCards.list_all",
        return_value=data["get_all_corporate_cards"],
    )

    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/refresh_dimensions/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    fyle_credentials = FyleCredential.objects.get(workspace_id=1)
    fyle_credentials.delete()

    response = api_client.post(url)

    assert response.status_code == 400
    assert response.data["message"] == "Fyle credentials not found in workspace"


def test_expense_group_sync(api_client, test_connection, mocker):
    mocker.patch(
        "fyle_integrations_platform_connector.apis.Expenses.get",
        return_value=data["expenses"],
    )
    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/expense_groups/sync/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_exportable_expense_group(api_client, test_connection, mocker):
    access_token = test_connection.access_token

    url = "/api/workspaces/1/fyle/exportable_expense_groups/"

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
