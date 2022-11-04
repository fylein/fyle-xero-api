import json
from unittest import mock
from apps.tasks.models import TaskLog
from apps.workspaces.models import XeroCredentials
from apps.fyle.models import Reimbursement
from .fixtures import data
from ..test_fyle.fixtures import data as fyle_data
from xerosdk.exceptions import InvalidGrant, InvalidTokenError, UnsuccessfulAuthentication 

def test_get_token_health(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/token_health/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    xero_credential = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_credential.delete()

    response = api_client.get(url)
    assert response.status_code == 400

    response = json.loads(response.content)
    assert response['message'] == 'Xero credentials not found in workspace'

    with mock.patch('apps.xero.utils.XeroConnector') as mock_call:
        mock_call.side_effect = InvalidGrant(msg='Invalid grant')
        response = api_client.get(url)
        assert response.status_code == 400

    with mock.patch('apps.xero.utils.XeroConnector') as mock_call:
        mock_call.side_effect = InvalidTokenError(msg='Invalid token error')
        response = api_client.get(url)
        assert response.status_code == 400

    with mock.patch('apps.xero.utils.XeroConnector') as mock_call:
        mock_call.side_effect = UnsuccessfulAuthentication(msg='Auth error')
        response = api_client.get(url)
        assert response.status_code == 400


def test_get_account_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/accounts/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 56


def test_post_account_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_accounts',
        return_value=None
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/accounts/'.format(workspace_id)

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


def test_get_bank_account_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/bank_accounts/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 2


def test_post_bank_account_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_accounts',
        return_value=None
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/bank_accounts/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 405

    response = json.loads(response.content)
    assert response['message'] == 'Method Not Allowed'


def test_get_tracking_categories_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/tracking_categories/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 0


def test_post_tracking_categories_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_tracking_categories',
        return_value=None
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/tracking_categories/'.format(workspace_id)

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


def test_get_contact_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/contacts/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 48


def test_post_contact_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_contacts',
        return_value=None
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/contacts/'.format(workspace_id)

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


def test_get_item_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/items/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 16


def test_post_item_view(mocker, api_client, test_connection):
    mocker.patch(
        'xerosdk.apis.Items.get_all',
        return_value={'Items': []}
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/items/'.format(workspace_id)

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


def test_export_trigger_view(api_client, test_connection):
    workspace_id = 1

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.save()

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/exports/trigger/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(
        url,
        data={
            'expense_group_ids': {
                'personal': [4],
                'ccc': [5]
                },
            'task_log_id': task_log.id
        },
        format='json'
        )
    assert response.status_code == 200


def test_post_payment_view(mocker, api_client, test_connection):
    mocker.patch(
        'xerosdk.apis.Payments.post',
        return_value = []
    )
    workspace_id = 1

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Reimbursements.list_all',
        return_value=fyle_data['get_all_reimbursements']
    )

    mocker.patch(
        'apps.xero.tasks.check_expenses_reimbursement_status',
        return_value = []
    )
    
    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/payments/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 0


def test_post_reimburse_payments(mocker, api_client, test_connection):
    mocker.patch(
        'xerosdk.apis.Invoices.post',
        return_value=data['bill_object']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Reimbursements.list_all',
        return_value=fyle_data['get_all_reimbursements']
    )
    
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.bulk_post_reimbursements',
        return_value=[]
    )

    mocker.patch(
        'xerosdk.apis.Invoices.get_by_id',
        return_value=data['bill_object']
    )

    workspace_id = 1

    Reimbursement.objects.all().delete()
    
    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/reimburse_payments/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_post_sync_dimensions(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_dimensions',
        return_value=None
    )
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/sync_dimensions/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.post(url)
    assert response.status_code == 200


def test_post_refresh_dimensions(mocker, api_client, test_connection):
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_dimensions',
        return_value=None
    )
    workspace_id = 1

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


def test_get_tax_code_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/tax_codes/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 8


def test_get_destination_attributes_view(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/xero/destination_attributes/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(
        url,
        data={
            'attribute_types': ['CUSTOMER']
        }
        )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert len(response) == 14
