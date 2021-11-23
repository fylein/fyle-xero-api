"""
API base class
"""

import json
import requests

from ..exceptions import *


class ApiBase:
    """
    Base class for all API classes
    """

    def __init__(self):
        self.__access_token = None
        self.__tenant_id = None
        self.__server_url = None

    def change_access_token(self, access_token):
        """
        Change old access token with a new one
        Parameters:
            access_token (str): New access token
        """

        self.__access_token = access_token

    def set_server_url(self, server_url):
        """
        Set server URL while creating a connection

        Parameters:
            server_url (str): Server URL for Xero API
        """

        self.__server_url = server_url

    def set_tenant_id(self, tenant_id):
        """
        Set tenant id while creating connection
        Parameters:
            tenant_id (str): Xero tenant ID
        """

        self.__tenant_id = tenant_id

    def _search_request(self, api_url, parameter: str, value: str):
        """
        HTTP get request to a given Xero API URL

        Parameters:
            api_url (str): URL of Xero API
            additional_headers (dict): HTTP Additional headers for the wanted API.
        """

        api_headers = {
            'authorization': 'Bearer ' + self.__access_token,
            'xero-tenant-id': self.__tenant_id,
            'accept': 'application/json'
        }

        api_url = '{0}?where={1}="{2}"'.format(api_url, parameter, value)

        response = requests.get(
            self.__server_url+api_url,
            headers=api_headers
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            return result

        if response.status_code == 403:
            raise UnsuccessfulAuthentication(
                'Invalid xero tenant ID or xero-tenant-id header missing'
            )

        if response.status_code == 429:
            error_msg = json.loads(response.text)
            raise RateLimitError('Too many requests', error_msg)

        if response.status_code == 500:
            raise InternalServerError(
                'Internal server error'
            )

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )

    def _get_request(self, api_url, page = None, additional_headers: dict = {}):
        """
        HTTP get request to a given Xero API URL

        Parameters:
            api_url (str): URL of Xero API
            page (int): Page number
            additional_headers (dict): HTTP Additional headers for the wanted API.
        """

        api_headers = {
            'authorization': 'Bearer ' + self.__access_token,
            'xero-tenant-id': self.__tenant_id,
            'accept': 'application/json',
            **additional_headers
        }

        api_url = '{0}?page={1}'.format(api_url, page)
        response = requests.get(
            self.__server_url+api_url,
            headers=api_headers
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            return result

        if response.status_code == 403:
            raise UnsuccessfulAuthentication(
                'Invalid xero tenant ID or xero-tenant-id header missing'
            )

        if response.status_code == 429:
            error_msg = json.loads(response.text)
            raise RateLimitError('Too many requests', error_msg)

        if response.status_code == 500:
            raise InternalServerError(
                'Internal server error'
            )

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )

    def _get_all_generator(self, api_url: str, attribute_type: str, additional_headers: dict = {}):
        """
        HTTP get request to a given Xero API URL

        Parameters:
            api_url (str): URL of Xero API
            attribute_type: API calling Attribute
        """
        page = 1
        has_more = True

        while has_more:
            response = self._get_request(api_url, page, additional_headers)
            page += 1
            yield response

            if not response[attribute_type]:
                has_more = False

    def _update_request(self, data, api_url):
        """
        HTTP put method to send data to Xero API URL

        Parameters:
            data (dict): Data to be sent to Xero API
            api_url (str): URL of Xero API
        """

        api_headers = {
            'Authorization': 'Bearer ' + self.__access_token,
            'xero-tenant-id': self.__tenant_id,
            'accept': 'application/json'
        }

        response = requests.put(
            self.__server_url + api_url,
            headers=api_headers,
            json=data
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            return result

        if response.status_code == 400:
            error_msg = json.loads(response.text)
            raise WrongParamsError(error_msg, response.status_code)

        if response.status_code == 401:
            error_msg = json.loads(response.text)
            raise InvalidTokenError('Invalid token, try to refresh it', error_msg)

        if response.status_code == 403:
            error_msg = json.loads(response.text)
            raise NoPrivilegeError('Forbidden, the user has insufficient privilege', error_msg)

        if response.status_code == 404:
            error_msg = json.loads(response.text)
            raise NotFoundItemError('Not found item with ID', error_msg)

        if response.status_code == 429:
            error_msg = json.loads(response.text)
            raise RateLimitError('Too many requests', error_msg)

        if response.status_code == 500:
            error_msg = json.loads(response.text)
            raise InternalServerError('Internal server error', error_msg)

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )

    def _post_request(self, data, api_url):
        """
        HTTP post method to send data to Xero API URL

        Parameters:
            data (dict): Data to be sent to Xero API
            api_url (str): URL of Xero API
        """

        api_headers = {
            'Authorization': 'Bearer ' + self.__access_token,
            'xero-tenant-id': self.__tenant_id,
            'accept': 'application/json'
        }

        response = requests.post(
            self.__server_url + api_url,
            headers=api_headers,
            json=data
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            return result

        if response.status_code == 400:
            error_msg = json.loads(response.text)
            raise WrongParamsError(error_msg, response.status_code)

        if response.status_code == 401:
            error_msg = json.loads(response.text)
            raise InvalidTokenError('Invalid token, try to refresh it', error_msg)

        if response.status_code == 403:
            error_msg = json.loads(response.text)
            raise NoPrivilegeError('Forbidden, the user has insufficient privilege', error_msg)

        if response.status_code == 404:
            error_msg = json.loads(response.text)
            raise NotFoundItemError('Not found item with ID', error_msg)

        if response.status_code == 429:
            print('this is the response text', response.text)
            # error_msg = json.loads(response.text)
            raise RateLimitError('Too many requests')

        if response.status_code == 500:
            error_msg = json.loads(response.text)
            raise InternalServerError('Internal server error', error_msg)

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )

    def _delete_request(self, api_url: str):
        """
        HTTP delete method to send data to Xero API URL

        Parameters:
            api_url (str): URL of Xero API
        """
        api_headers = {
            'authorization': 'Bearer ' + self.__access_token,
        }
        response = requests.delete(
            self.__server_url + api_url,
            headers=api_headers
        )

        if response.status_code == 200:
            return json.loads(response.text)

        if response.status_code == 204:
            return None

        if response.status_code == 400:
            error_msg = json.loads(response.text)
            raise WrongParamsError(error_msg, response.status_code)

        if response.status_code == 401:
            error_msg = json.loads(response.text)
            raise InvalidTokenError('Invalid token, try to refresh it', error_msg)

        if response.status_code == 403:
            error_msg = json.loads(response.text)
            raise NoPrivilegeError('Forbidden, the user has insufficient privilege', error_msg)

        if response.status_code == 404:
            error_msg = json.loads(response.text)
            raise NotFoundItemError('Not found item with ID', error_msg)

        if response.status_code == 429:
            error_msg = json.loads(response.text)
            raise RateLimitError('Too many requests', error_msg)

        if response.status_code == 500:
            error_msg = json.loads(response.text)
            raise InternalServerError('Internal server error', error_msg)

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )

    def _get_tenant_ids(self):
        api_headers = {
            'authorization': 'Bearer ' + self.__access_token,
        }
        response = requests.get('https://api.xero.com/connections', headers=api_headers)

        if response.status_code == 200:
            return json.loads(response.text)

        if response.status_code == 400:
            error_msg = json.loads(response.text)
            raise WrongParamsError(error_msg, response.status_code)

        if response.status_code == 401:
            error_msg = json.loads(response.text)
            raise InvalidTokenError('Invalid token, try to refresh it', error_msg)

        if response.status_code == 403:
            error_msg = json.loads(response.text)
            raise NoPrivilegeError('Forbidden, the user has insufficient privilege', error_msg)

        if response.status_code == 404:
            error_msg = json.loads(response.text)
            raise NotFoundItemError('Not found item with ID', error_msg)

        if response.status_code == 429:
            error_msg = json.loads(response.text)
            raise RateLimitError('Too many requests', error_msg)

        if response.status_code == 500:
            error_msg = json.loads(response.text)
            raise InternalServerError('Internal server error', error_msg)

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )

    def _post_attachment(self, data, api_url):
        """Create a HTTP post request.

        Parameters:
            data: Data to be sent to Xero API
            api_url (str): Url of the Xero API.

        Returns:
            A response from the request (dict).
        """

        api_headers = {
            'Authorization': 'Bearer {}'.format(self.__access_token),
            'xero-tenant-id': self.__tenant_id,
            'Accept': 'application/json',
            'Content-Type': '*'
        }
        response = requests.post(
            '{0}{1}'.format(self.__server_url, api_url),
            headers=api_headers,
            data=data
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            return result

        if response.status_code == 400:
            error_msg = response.text
            raise WrongParamsError(error_msg, response.status_code)

        if response.status_code == 401:
            error_msg = json.loads(response.text)
            raise InvalidTokenError('Invalid token, try to refresh it', error_msg)

        if response.status_code == 403:
            error_msg = response.text
            raise NoPrivilegeError('Forbidden, the user has insufficient privilege', error_msg)

        if response.status_code == 404:
            error_msg = json.loads(response.text)
            raise NotFoundItemError('Not found item with ID', error_msg)

        if response.status_code == 429:
            error_msg = json.loads(response.text)
            raise RateLimitError('Too many requests', error_msg)

        if response.status_code == 500:
            error_msg = json.loads(response.text)
            raise InternalServerError('Internal server error', error_msg)

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )
