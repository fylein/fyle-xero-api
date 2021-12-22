"""
Authentication utils
"""
import json
from typing import Dict

from django.conf import settings

import requests


def post_request(url, body, access_token: str = None, origin_address: str = None) -> Dict:
    """
    Create a HTTP post request.
    """
    api_headers = {
        'content-type': 'application/json',
        'X-Forwarded-For': origin_address
    }

    if access_token:
        api_headers['Authorization'] = 'Bearer {0}'.format(access_token)

    print('post_request', url, body, api_headers)

    response = requests.post(
        url,
        headers=api_headers,
        data=json.dumps(body)
    )

    print('response', response.status_code, response.text)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_request(url, access_token, origin_address: str = None):
    """
    Create a HTTP get request.
    """
    api_headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'X-Forwarded-For': origin_address
    }

    response = requests.get(
        url,
        headers=api_headers
    )

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


class AuthUtils:
    """
    Authentication utility functions
    """
    def __init__(self):
        self.base_url = settings.FYLE_BASE_URL
        self.token_url = settings.FYLE_TOKEN_URI
        self.client_id = settings.FYLE_CLIENT_ID
        self.client_secret = settings.FYLE_CLIENT_SECRET

    def generate_fyle_refresh_token(self, authorization_code: str) -> Dict:
        """
        Get refresh token from authorization code
        """
        api_data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code
        }

        return self.post(url=self.token_url, body=api_data)

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token
        """
        api_data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }

        return post_request(self.token_url, api_data)


    @staticmethod
    def get_origin_address(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
