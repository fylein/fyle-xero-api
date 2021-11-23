"""
Xero Accounts API
"""

from .api_base import ApiBase


class Accounts(ApiBase):
    """
    Class for Accounts API
    """

    GET_ACCOUNTS = '/api.xro/2.0/Accounts'

    def get_all(self, modified_after: str = None):
        """
        Get all accounts

        :param modified_after: Optional modified_after parameter as a string in 2009-11-12T00:00:00 format

        Returns:
            List of all accounts
        """

        return self._get_request(Accounts.GET_ACCOUNTS, additional_headers={'If-Modified-Since': modified_after})
