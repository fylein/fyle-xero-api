"""
Xero Items API
"""

from .api_base import ApiBase


class Items(ApiBase):
    """
    Class for Items API
    """

    GET_ITEMS = '/api.xro/2.0/Items'

    def get_all(self, modified_after: str = None):
        """
        Get all Items

        :param modified_after: Optional modified_after parameter as a string in 2009-11-12T00:00:00 format

        Returns:
            List of all Items
        """

        return self._get_request(Items.GET_ITEMS, additional_headers={'If-Modified-Since': modified_after})
