import os
from datetime import datetime, timezone
from unittest import mock
import pytest
from rest_framework.test import APIClient
from fyle_rest_auth.models import AuthToken, User
from fyle.platform import Platform

from apps.fyle.helpers import get_access_token
from fyle_xero_api.tests import settings
from .test_fyle.fixtures import data as fyle_data


def pytest_configure():
    os.system('sh ./tests/sql_fixtures/reset_db_fixtures/reset_db.sh')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture(request):
    patched_1 = mock.patch('xerosdk.XeroSDK.refresh_access_token')
    patched_1.__enter__()

    patched_2 = mock.patch(
        'fyle_rest_auth.authentication.get_fyle_admin',
        return_value=fyle_data['get_my_profile']
    )
    patched_2.__enter__()

    patched_3 = mock.patch(
        'fyle.platform.internals.auth.Auth.update_access_token',
        return_value='asnfalsnkflanskflansfklsan'
    )
    patched_3.__enter__()

    patched_4 = mock.patch(
        'apps.fyle.helpers.post_request',
        return_value={
            'access_token': 'easnfkjo12233.asnfaosnfa.absfjoabsfjk',
            'cluster_domain': 'https://staging.fyle.tech'
        }
    )
    patched_4.__enter__()

    patched_5 = mock.patch(
        'fyle.platform.apis.v1beta.spender.MyProfile.get',
        return_value=fyle_data['get_my_profile']
    )
    patched_5.__enter__()

    def unpatch():
        patched_1.__exit__()
        patched_2.__exit__()
        patched_3.__exit__()
        patched_4.__exit__()
        patched_5.__exit__()

    request.addfinalizer(unpatch)


@pytest.fixture()
def test_connection(db):
    """
    Creates a connection with Fyle
    """
    client_id = settings.FYLE_CLIENT_ID
    client_secret = settings.FYLE_CLIENT_SECRET
    token_url = settings.FYLE_TOKEN_URI
    refresh_token = settings.FYLE_REFRESH_TOKEN
    server_url = settings.FYLE_SERVER_URL

    fyle_connection = Platform(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        server_url=server_url
    )

    access_token = get_access_token(refresh_token)
    fyle_connection.access_token = access_token
    user_profile = fyle_connection.v1beta.spender.my_profile.get()['data']
    user = User(
        password='', last_login=datetime.now(tz=timezone.utc), id=1, email=user_profile['user']['email'],
        user_id=user_profile['user_id'], full_name='', active='t', staff='f', admin='t'
    )

    user.save()

    auth_token = AuthToken(
        id=1,
        refresh_token=refresh_token,
        user=user
    )
    auth_token.save()

    return fyle_connection
