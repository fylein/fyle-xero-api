import json
from unittest import mock
from datetime import datetime
from apps.mappings.models import TenantMapping
from fyle_accounting_mappings.models import Mapping 
from fyle_xero_api import settings
from django.contrib.auth import get_user_model
from fyle_rest_auth.utils import AuthUtils
from tests.helper import dict_compare_keys
from xerosdk import exceptions as xero_exc
from fyle.platform import exceptions as fyle_exc
from apps.workspaces.models import Workspace, WorkspaceSchedule, WorkspaceGeneralSettings, XeroCredentials, LastExportDetail
from .fixtures import data
from ..test_xero.fixtures import data as xero_data
from ..test_fyle.fixtures import data as fyle_data

User = get_user_model()
auth_utils = AuthUtils()


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


def test_post_of_workspace(api_client, test_connection, mocker):
    workspace_id = 1

    url = '/api/workspaces/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    mocker.patch(
        'apps.workspaces.views.get_fyle_admin',
        return_value=fyle_data['get_my_profile']
    )

    mocker.patch(
        'apps.workspaces.views.get_cluster_domain',
        return_value={
            'cluster_domain': 'https://staging.fyle.tech/'
        }
    )
    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'

    mocker.patch(
        'apps.workspaces.views.get_fyle_admin',
        return_value=fyle_data['get_exsisting_org']
    )

    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'

    url = '/api/workspaces/{}/'.format(workspace_id)

    response = api_client.patch(url)
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace']) == [], 'workspaces api returns a diff in the keys'


def test_connect_xero_view_post(mocker, api_client, test_connection):
    workspace_id = 1
    tenant_mapping = TenantMapping.objects.filter(workspace_id=workspace_id).first()

    mocker.patch(
        'apps.workspaces.views.generate_xero_refresh_token',
        return_value='asdfghjk'
    )

    mocker.patch(
        'xerosdk.apis.Connections.get_all',
        return_value=[{'tenantId': tenant_mapping.tenant_id, 'id': 'asdfghjkl'}]
    )

    mocker.patch(
        'xerosdk.apis.Organisations.get_all',
        return_value=xero_data['get_all_organisations']
    )

    code = 'asdfghj'
    url = '/api/workspaces/{}/connect_xero/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(
        url,
        data={
            'code': code
        }    
    )
    assert response.status_code == 200

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_credentials.delete()

    with mock.patch('apps.xero.utils.XeroConnector.get_organisations') as mock_call:
        mock_call.side_effect = xero_exc.WrongParamsError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')
        response = api_client.post(
            url,
            data={
                'code': code,
                'redirect_uri': 'ffff.fff.fff'
            }    
        )
        assert response.status_code == 200


def test_connect_xero_view_exceptions(api_client, test_connection):
    workspace_id = 1
    
    code = 'qwertyu'
    url = '/api/workspaces/{}/connect_xero/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    with mock.patch('apps.workspaces.views.generate_xero_refresh_token') as mock_call:
        mock_call.side_effect = xero_exc.InvalidClientError(msg='Invalid client', response=json.dumps({'message': 'Invalid client'}))
        
        response = api_client.post(
            url,
            data={
                'code': code
            }    
        )
        assert response.status_code == 400

        mock_call.side_effect = xero_exc.InvalidGrant(msg='invalid grant', response=json.dumps({'message': 'invalid grant'}))
        
        response = api_client.post(
            url,
            data={
                'code': code
            }
        )
        assert response.status_code == 400

        mock_call.side_effect = xero_exc.InvalidTokenError(msg='Invalid token', response='Invalid token')
        
        response = api_client.post(
            url,
            data={
                'code': code
            }
        )
        assert response.status_code == 401

        mock_call.side_effect = xero_exc.InternalServerError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')
        
        response = api_client.post(
            url,
            data={
                'code': code
            }   
        )
        assert response.status_code == 500

def test_connect_xero_view(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/credentials/xero/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 200

    XeroCredentials.objects.filter(workspace_id=workspace_id).delete()

    response = api_client.get(url)
    assert response.status_code == 400


def test_revoke_xero_connection(mocker, api_client, test_connection):
    mocker.patch(
        'xerosdk.apis.Connections.remove_connection',
        return_value=None
    )

    workspace_id = 1
    workspace = Workspace.objects.filter(id=workspace_id).first()
    workspace.onboarding_state = 'CONNECTION'
    workspace.save()
    
    url = '/api/workspaces/{}/connection/xero/revoke/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.connection_id = 'sdfghjkl'
    tenant_mapping.save()

    Mapping.objects.filter(workspace_id=workspace_id).delete()

    response = api_client.post(url)
    assert response.status_code == 200

    with mock.patch('xerosdk.apis.Connections.remove_connection') as mock_call:
        mock_call.side_effect = xero_exc.InternalServerError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')
        
        response = api_client.post(url)
        assert response.status_code == 200


def test_get_general_settings_detail(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/settings/general/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_setting.import_customers = True
    workspace_general_setting.save()

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

    workspace_general_setting.delete()

    response = api_client.get(url)
    assert response.status_code == 400


def test_xero_external_signup_view(mocker, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.generate_xero_identity',
        return_value={}
    )
    url = '/api/workspaces/external_signup/'
    code = 'sdfghjk'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(
        url,
        data = {
            'code': code,
            'redirect_uri': settings.XERO_REDIRECT_URI
        })
    assert response.status_code == 200


def test_export_to_xero(mocker, api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/exports/trigger/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    last_export_detail = LastExportDetail.objects.create(workspace_id=workspace_id)

    response = api_client.post(url)
    assert response.status_code == 200


def test_last_export_detail(mocker, api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/export_detail/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)
    assert response.status_code == 400

    last_export_detail = LastExportDetail.objects.create(workspace_id=workspace_id)
    last_export_detail.last_exported_at = datetime.now()
    last_export_detail.total_expense_groups_count = 1
    last_export_detail.save()

    response = api_client.get(url)
    assert response.status_code == 200
