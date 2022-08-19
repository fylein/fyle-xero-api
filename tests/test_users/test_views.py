from django.urls import reverse


def test_get_profile_view(api_client, test_connection):
    access_token = test_connection.access_token

    url = '/api/user/profile/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200


def test_get_fyle_orgs_view(api_client, test_connection):
    access_token = test_connection.access_token
    
    url = '/api/user/orgs/'
    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url)
    assert response.status_code == 200
