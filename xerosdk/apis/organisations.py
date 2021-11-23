"""
Xero Organisations API
"""

from .api_base import ApiBase


class Organisations(ApiBase):
    """
    Class for Organisations API
    """

    GET_ORGANISATIONS = '/api.xro/2.0/Organisation'

    def get_all(self):
        """
        Get Organisations

        Returns:
            List of Organisations
        """

        return self._get_request(Organisations.GET_ORGANISATIONS)['Organisations']
