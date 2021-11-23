"""
Xero Invoices API
"""

from .api_base import ApiBase


class Invoices(ApiBase):
    """
    Class for Invoices API
    """

    GET_INVOICES = '/api.xro/2.0/Invoices'
    GET_INVOICE_BY_ID = '/api.xro/2.0/invoices/{0}'
    POST_INVOICE = '/api.xro/2.0/invoices'

    def get_all(self):
        """
        Get all invoices

        Returns:
            List of all invoices
        """

        return self._get_request(Invoices.GET_INVOICES)

    def list_all_generator(self):
        """
        Get all invoices

        Returns:
            List of all invoices with pagination
        """

        return list(self._get_all_generator(Invoices.GET_INVOICES, 'Invoices'))

    def get_by_id(self, invoice_id):
        """
        Get invoice by invoice_id

        Parameters:
            invoice_id (str): Invoice ID

        Returns:
            Invoice dict
        """

        return self._get_request(Invoices.GET_INVOICE_BY_ID.format(invoice_id))

    def post(self, data):
        """
        Create new invoice

        Parameters:
            data (dict): Data to create invoice

        Returns:
             Response from API
        """

        return self._post_request(data, Invoices.POST_INVOICE)
