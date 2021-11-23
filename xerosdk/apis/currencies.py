"""
Xero Currencies API
"""

from .api_base import ApiBase


class Currencies(ApiBase):
    """
    Class for Currencies API
    """

    CURRENCIES = '/api.xro/2.0/Currencies'

    def get_all(self):
        """
        Get all Currencies

        Returns:
            List of all Currencies
        """

        return self._get_request(Currencies.CURRENCIES)


    def post(self, data: dict):
        """
        Create new currency

        Parameters:
            data (dict): Data to create currency

        Returns:
             Response from API
        """

        return self._update_request(data, Currencies.CURRENCIES)
