"""
Xero Connections API
"""

from .api_base import ApiBase


class Connections(ApiBase):
    """
    Class for Connections
    """
    GET_CONNECTIONS = '/connections'
    REVOKE_CONNECTION = '/connections/{}'

    def get_all(self):
        """
        Get all Connections

        Returns:
            List of all Connections
        """

        return self._get_request(Connections.GET_CONNECTIONS)


    def remove_connection(self, connection_id: str):
        """
        Remove tenant connection

        Parameters:
            connection_id (str): Connection ID
        """

        return self._delete_request(Connections.REVOKE_CONNECTION.format(connection_id))
