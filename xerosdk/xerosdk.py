"""
Xero SDK connection base class
"""

import base64
import json

import requests

from .apis import *
from .exceptions import *


class XeroSDK:
    """
    Creates connection with Xero APIs using OAuth2 authentication

    Parameters:
        base_url (str): Base URL for Xero API
        client_id (str): Client ID for Xero API
        client_secret (str): Client Secret for Xero API
        refresh_token (str): Refresh token for Xero API
    """

    TOKEN_URL = 'https://identity.xero.com/connect/token'
    AUTHORIZE_URL = 'https://login.xero.com/identity/connect/authorize'

    def __init__(self, base_url, client_id, client_secret, refresh_token):
        # Store the input parameters
        self.__base_url = base_url
        self.__client_id = client_id
        self.__client_secret = client_secret
        self._refresh_token = refresh_token  # Fix: refresh token expiry

        # Create an object for each API
        self.invoices = Invoices()
        self.accounts = Accounts()
        self.contacts = Contacts()
        self.tracking_categories = TrackingCategories()
        self.payments = Payments()
        self.items = Items()
        self.tenants = Tenants()
        self.bank_transactions = BankTransactions()
        self.attachments = Attachments()
        self.organisations = Organisations()
        self.connections = Connections()
        self.currencies = Currencies()

        # Set the server url
        self.set_server_url()

        # Refresh access token
        self.refresh_access_token()

    def set_server_url(self):
        """
        Set server URL for all API objects
        """

        base_url = self.__base_url

        self.invoices.set_server_url(base_url)
        self.accounts.set_server_url(base_url)
        self.contacts.set_server_url(base_url)
        self.tracking_categories.set_server_url(base_url)
        self.items.set_server_url(base_url)
        self.tenants.set_server_url(base_url)
        self.payments.set_server_url(base_url)
        self.bank_transactions.set_server_url(base_url)
        self.attachments.set_server_url(base_url)
        self.organisations.set_server_url(base_url)
        self.connections.set_server_url(base_url)
        self.currencies.set_server_url(base_url)

    def set_tenant_id(self, tenant_id):
        """
        Set tenant id for all API objects

        Parameters:
            tenant_id (str): Xero tenant ID
        """

        self.invoices.set_tenant_id(tenant_id)
        self.accounts.set_tenant_id(tenant_id)
        self.contacts.set_tenant_id(tenant_id)
        self.tracking_categories.set_tenant_id(tenant_id)
        self.items.set_tenant_id(tenant_id)
        self.payments.set_tenant_id(tenant_id)
        self.tenants.set_tenant_id(tenant_id)
        self.bank_transactions.set_tenant_id(tenant_id)
        self.attachments.set_tenant_id(tenant_id)
        self.organisations.set_tenant_id(tenant_id)
        self.connections.set_tenant_id(tenant_id)
        self.currencies.set_tenant_id(tenant_id)

    def refresh_access_token(self):
        """
        Refresh access token for each API objects
        """

        access_token = self.__get_access_token()

        self.invoices.change_access_token(access_token)
        self.accounts.change_access_token(access_token)
        self.contacts.change_access_token(access_token)
        self.tracking_categories.change_access_token(access_token)
        self.items.change_access_token(access_token)
        self.payments.change_access_token(access_token)
        self.tenants.change_access_token(access_token)
        self.bank_transactions.change_access_token(access_token)
        self.attachments.change_access_token(access_token)
        self.organisations.change_access_token(access_token)
        self.connections.change_access_token(access_token)
        self.currencies.change_access_token(access_token)

    def __get_access_token(self):
        """
        Get access token from Xero TOKEN_URL

        Returns:
            A new access token
        """

        api_headers = {
            'authorization': 'Basic ' + str(
                base64.b64encode(
                    (self.__client_id + ':' + self.__client_secret).encode('utf-8')
                ), 'utf-8'
            ),
        }
        api_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token  # Fix: refresh token expiry
        }
        response = requests.post(XeroSDK.TOKEN_URL, headers=api_headers, data=api_data)

        if response.status_code == 200:
            token = json.loads(response.text)
            self._refresh_token = token['refresh_token']  # Fix: refresh token expiry
            return token['access_token']

        error_msg = json.loads(response.text)['error']
        if response.status_code == 400:
            if error_msg == 'invalid_client':
                raise InvalidClientError(
                    'Invalid client ID or client secret or refresh token'
                )

            if error_msg == 'invalid_grant':
                raise InvalidGrant(
                    'Invalid refresh token'
                )

            if error_msg == 'unsupported_grant_type':
                raise UnsupportedGrantType(
                    'Invalid or non-existing grant type in request body'
                )

            raise XeroSDKError(
                'Status code {0}'.format(response.status_code), response.text
            )

        if response.status_code == 500:
            raise InternalServerError(
                'Internal server error'
            )

        raise XeroSDKError(
            'Status code {0}'.format(response.status_code), response.text
        )

    @property
    def refresh_token(self):
        """
        Get the refresh_token
        """
        return self._refresh_token
