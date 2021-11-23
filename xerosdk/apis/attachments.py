"""
Xero Attachments API
"""
from typing import BinaryIO

from .api_base import ApiBase


class Attachments(ApiBase):
    """Class for Attachments APIs."""

    GET_ATTACHMENT = '/api.xro/2.0/{0}/{1}/attachments'
    POST_ATTACHMENT = '/api.xro/2.0/{0}/{1}/attachments/{2}'

    def get_attachments(self, endpoint, guid):
        """Get the list of attachments

        Parameters:
            :param endpoint: The name of the parent endpoint (e.g. Receipts, Invoices)
            :param guid: The guid of the document that that attachment belongs to (e.g. ReceiptID or InvoiceID)

        Returns:
            List with dicts in Attachments schema.
        """
        return self._get_request(self.GET_ATTACHMENT.format(endpoint, guid))

    def post_attachment(self, endpoint, guid, filename, data: BinaryIO):
        """

        Parameters:
            :param data: Raw image content
            :param endpoint: The name of the parent endpoint (e.g. Receipts, Invoices)
            :param guid: The guid of the document that that attachment belongs to (e.g. ReceiptID or InvoiceID)
            :param filename: Name of the attachment

        Returns:
        """
        return self._post_attachment(data, self.POST_ATTACHMENT.format(endpoint, guid, filename))
