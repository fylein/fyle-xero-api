import json
import requests
import unittest
from unittest.mock import MagicMock, patch, Mock
from unittest import mock
from requests.models import Response
from apps.mappings.models import TenantMapping
from apps.xero.utils import XeroConnector, XeroCredentials
from fyle_xero_api import settings
from django.contrib.auth import get_user_model
from fyle_rest_auth.utils import AuthUtils
from tests.helper import dict_compare_keys
from xerosdk import exceptions as xero_exc
from fyle.platform import exceptions as fyle_exc
from apps.workspaces.models import Workspace, WorkspaceSchedule, WorkspaceGeneralSettings
from .fixtures import data
from apps.workspaces.utils import generate_xero_refresh_token

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


def test_post_of_workspace(api_client, test_connection):

    url = '/api/workspaces/'

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.post(url)
    assert response.status_code == 200

    response = json.loads(response.content)
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


def test_connect_fyle_view_post(mocker, api_client, test_connection):
    mocker.patch(
        'fyle_rest_auth.utils.AuthUtils.generate_fyle_refresh_token',
        return_value={'refresh_token': 'asdfghjk', 'access_token': 'qwertyuio'}
    )
    mocker.patch(
        'apps.workspaces.views.get_fyle_admin',
        return_value={'data': {'org': {'name': 'FAE', 'id': 'orPJvXuoLqvJ'}}}
    )
    mocker.patch(
        'apps.workspaces.views.get_cluster_domain',
        return_value='https://staging.fyle.tech'
    )
    workspace_id = 1

    code = 'sdfghj'
    url = '/api/workspaces/{}/connect_fyle/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.post(
            url,
            data={'code': code}    
        )
    assert response.status_code == 200


def test_connect_fyle_view_exceprions(api_client, test_connection):
    workspace_id = 1
    
    code = 'qwertyu'
    url = '/api/workspaces/{}/connect_fyle/authorization_code/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    with mock.patch('fyle_rest_auth.utils.AuthUtils.generate_fyle_refresh_token') as mock_call:
        mock_call.side_effect = fyle_exc.UnauthorizedClientError(msg='Invalid Authorization Code', response='Invalid Authorization Code')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 403

        mock_call.side_effect = fyle_exc.NotFoundClientError(msg='Fyle Application not found', response='Fyle Application not found')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 404

        mock_call.side_effect = fyle_exc.WrongParamsError(msg='Some of the parameters are wrong', response='Some of the parameters are wrong')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 400

        mock_call.side_effect = fyle_exc.InternalServerError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 401


def test_connect_xero_view(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/credentials/xero/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 200

    response = json.loads(response.content)

    url = '/api/workspaces/{}/credentials/xero/delete/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.delete(url)
    assert response.status_code == 200

    url = '/api/workspaces/{}/credentials/xero/'.format(workspace_id)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    response = api_client.get(url)
    assert response.status_code == 400


def test_connect_xero_view_post(mocker, api_client, test_connection):
    mocker.patch(
        'apps.workspaces.views.generate_xero_refresh_token',
        return_value='asdfghjk'
    )
    workspace_id = 1

    code = 'asdfghj'
    url = '/api/workspaces/{}/connect_xero/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    response = api_client.post(
        url,
        data={'code': code}    
    )

    response = api_client.post(url)
    assert response.status_code == 200


def test_connect_xero_view_exceprions(api_client, test_connection):
    workspace_id = 1
    
    code = 'qwertyu'
    url = '/api/workspaces/{}/connect_xero/authorization_code/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))
    
    with mock.patch('apps.workspaces.views.generate_xero_refresh_token') as mock_call:
        mock_call.side_effect = xero_exc.InvalidClientError(msg='Invalid client', response=json.dumps({'message': 'Invalid client'}))
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 400

        mock_call.side_effect = xero_exc.InvalidGrant(msg='invalid grant', response=json.dumps({'message': 'invalid grant'}))
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 400

        mock_call.side_effect = xero_exc.InvalidTokenError(msg='Invalid token', response='Invalid token')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 401

        mock_call.side_effect = xero_exc.InternalServerError(msg='Wrong/Expired Authorization code', response='Wrong/Expired Authorization code')
        
        response = api_client.post(
            url,
            data={'code': code}    
        )
        assert response.status_code == 500


def test_revoke_xero_connection(mocker, api_client, test_connection):
    mocker.patch(
        'xerosdk.apis.Connections.remove_connection',
        return_value=None
    )
    workspace_id = 1
    
    url = '/api/workspaces/{}/connection/xero/revoke/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.connection_id = 'sdfghjkl'
    tenant_mapping.save()

    response = api_client.post(url)
    assert response.status_code == 200


def test_workspace_schedule(api_client, test_connection):
    workspace_id = 1

    url = '/api/workspaces/{}/schedule/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(test_connection.access_token))

    response = api_client.get(url)

    WorkspaceSchedule.objects.get_or_create(
        workspace_id=workspace_id
    )
    response = api_client.get(url)

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace_schedule']) == [], 'workspace_schedule api returns a diff in keys'

    response = api_client.post(
        url,
        data={
            'schedule_enabled': True,
            'hours': 1
        },
        format='json'    
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert dict_compare_keys(response, data['workspace_schedule']) == [], 'workspace_schedule api returns a diff in keys'


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
