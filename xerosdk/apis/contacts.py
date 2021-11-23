"""
Xero Contacts API
"""

from .api_base import ApiBase


class Contacts(ApiBase):
    """
    Class for Contacts API
    """

    GET_CONTACTS = '/api.xro/2.0/Contacts'
    POST_CONTACTS = '/api.xro/2.0/Contacts'

    def get_all(self, modified_after: str = None):
        """
        Get all contacts

        :param modified_after: Optional modified_after parameter as a string in 2009-11-12T00:00:00 format

        Returns:
            List of all contacts
        """

        return self._get_request(Contacts.GET_CONTACTS, additional_headers={'If-Modified-Since': modified_after})

    def list_all_generator(self, modified_after: str = None):
        """
        Get all contacts

        :param modified_after: Optional modified_after parameter as a string in 2009-11-12T00:00:00 format

        Returns:
            List of all contacts with pagination
        """

        return list(self._get_all_generator(
            Contacts.GET_CONTACTS, 'Contacts', additional_headers={'If-Modified-Since': modified_after}))

    def post(self, data):
        """
        create new contact

        Parameters:
        data (dict): Data to create contact

        Returns:
             Response from API
        """

        return self._post_request(data, Contacts.POST_CONTACTS)

    def search_contact_by_contact_name(self, contact_name: str):
        """
        Search contact by Contact Name
        :param contact_name: Xero Contact Name
        :return: Contact
        """

        response = self._search_request(Contacts.GET_CONTACTS, 'Name', contact_name)

        return response['Contacts'][0] if response['Contacts'] else None
