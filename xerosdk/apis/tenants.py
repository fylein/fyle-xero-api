"""
Xero Tenants API
"""

from .api_base import ApiBase


class Tenants(ApiBase):
    """
    Class for Tenants
    """

    def get_all(self):
        """
        Get all Tenants

        Returns:
            List of all Tenants
        """

        return self._get_tenant_ids()
