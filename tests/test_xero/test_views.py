import json

from fyle_accounting_mappings.models import MappingSetting
from xerosdk import exceptions as xero_exc

from apps.workspaces.models import Workspace, XeroCredentials


def test_get_token_health(mocker, api_client, test_connection):
    workspace_id = 1
    mocker.patch("apps.xero.utils.XeroConnector.__init__", return_value=None)
    mocker.patch("apps.xero.utils.XeroConnector.get_organisations", return_value=['organization_1', 'organization_2'])

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/token_health/".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    XeroCredentials.objects.filter(workspace_id=workspace_id).delete()
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Xero credentials not found"

    XeroCredentials.objects.filter(workspace_id=workspace_id).delete()
    XeroCredentials.objects.create(workspace_id=workspace_id,refresh_token=None,is_expired=True)
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Xero connection expired"

    XeroCredentials.objects.filter(workspace_id=workspace_id).delete()
    XeroCredentials.objects.create(workspace_id=workspace_id,refresh_token=None,is_expired=False)
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Xero disconnected"

    XeroCredentials.objects.filter(workspace_id=workspace_id).delete()
    XeroCredentials.objects.create(workspace_id=workspace_id,refresh_token="dummy_refresh_token",is_expired=False)
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['message'] == "Xero connection is active"

    # for InvalidTokenError
    mocker.patch("apps.xero.utils.XeroConnector.get_organisations", side_effect=xero_exc.InvalidTokenError("Token expired"))
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Xero connection expired"

    mocker.patch("apps.xero.utils.XeroConnector.get_organisations", side_effect=xero_exc.WrongParamsError("Wrong parameters"))
    response = api_client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == "Xero connection expired"


def test_token_health_wrong_params_error_coverage(mocker, api_client, test_connection):
    """
    test to cover TokenHealthView for WrongParamsError
    """
    workspace_id = 1
    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/token_health/".format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    XeroCredentials.objects.filter(workspace_id=workspace_id).delete()
    XeroCredentials.objects.create(workspace_id=workspace_id, refresh_token="dummy_refresh_token", is_expired=False)

    mock_logger = mocker.patch("apps.xero.views.logger")

    mocker.patch("apps.xero.utils.XeroConnector.__init__", return_value=None)
    mocker.patch("apps.xero.utils.XeroConnector.get_organisations", side_effect=xero_exc.WrongParamsError("Wrong params"))

    def passthrough_decorator():
        def decorator(func):
            def new_fn(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except xero_exc.WrongParamsError:
                    raise
                except Exception as e:
                    from rest_framework.response import Response
                    from rest_framework.views import status
                    return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return new_fn
        return decorator

    mocker.patch("apps.xero.views.handle_view_exceptions", side_effect=passthrough_decorator)
    response = api_client.get(url)
    mock_logger.error.assert_called_once_with(
        "Xero wrong params error for workspace_id %s",
        workspace_id,
        exc_info=True
    )

    assert response.status_code == 400
    assert response.data['message'] == "Something went wrong"


def test_get_tenant_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/tenants/?attribute_type=TENANT".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 1


def test_post_tenant_view(mocker, api_client, test_connection):
    mocker.patch("xerosdk.apis.Tenants.get_all", return_value=[])
    workspace_id = 1

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/tenants/".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 0

    xero_credential = XeroCredentials.get_active_xero_credentials(
        workspace_id=workspace_id
    )
    xero_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response["message"] == "Xero credentials not found in workspace"


def test_get_xero_fields_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/xero_fields/".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 3


def test_post_sync_dimensions(mocker, api_client, test_connection):
    mocker.patch("apps.xero.utils.XeroConnector.sync_dimensions", return_value=None)
    mocker.patch("apps.xero.views.publish_to_rabbitmq")
    workspace_id = 1

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/sync_dimensions/".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    workspace = Workspace.objects.get(id=workspace_id)
    destination_synced_at = workspace.destination_synced_at

    response = api_client.post(url)
    assert response.status_code == 200

    workspace.destination_synced_at = destination_synced_at
    workspace.save()

    xero_credential = XeroCredentials.get_active_xero_credentials(
        workspace_id=workspace_id
    )
    xero_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response["message"] == "Xero credentials not found in workspace"


def test_post_refresh_dimensions(mocker, api_client, test_connection):
    mocker.patch("apps.xero.utils.XeroConnector.sync_dimensions", return_value=None)
    mocker.patch("apps.xero.views.publish_to_rabbitmq")
    expense_field_mock = mocker.patch("apps.mappings.signals.ExpenseCustomField")
    expense_field_mock.return_value.sync_expense_attributes.return_value = []

    workspace_id = 1

    MappingSetting.objects.update_or_create(
        workspace_id=workspace_id,
        source_field="PROJECT",
        defaults={"destination_field": "CUSTOMER", "import_to_fyle": True},
    )

    MappingSetting.objects.update_or_create(
        workspace_id=workspace_id,
        source_field="COST_CENTER",
        defaults={"destination_field": "ACCOUNT", "import_to_fyle": True},
    )

    MappingSetting.objects.update_or_create(
        workspace_id=workspace_id,
        source_field="Ashutosh Field",
        defaults={
            "destination_field": "CLASS",
            "import_to_fyle": True,
            "is_custom": True,
        },
    )

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/refresh_dimensions/".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    xero_credential = XeroCredentials.get_active_xero_credentials(
        workspace_id=workspace_id
    )
    xero_credential.delete()

    response = api_client.post(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response["message"] == "Xero credentials not found in workspace"


def test_get_destination_attributes_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = "/api/workspaces/{}/xero/destination_attributes/".format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION="Bearer {}".format(access_token))

    response = api_client.get(
        url, data={"attribute_type__in": "CUSTOMER", "active": "true"}
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 0
