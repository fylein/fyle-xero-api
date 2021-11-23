"""
Xero Bank Transactions API
"""

from .api_base import ApiBase


class BankTransactions(ApiBase):
    """
    Class for Bank Transactions API
    """

    GET_BANK_TRANSACTIONS = '/api.xro/2.0/banktransactions'
    GET_BANK_TRANSACTION_BY_ID = '/api.xro/2.0/banktransactions/{0}'
    POST_BANK_TRANSACTION = '/api.xro/2.0/banktransactions'

    def get_all(self):
        """
        Get all Bank Transactions

        Returns:
            List of all Bank Transactions
        """

        return self._get_request(BankTransactions.GET_BANK_TRANSACTIONS)

    def list_all_generator(self):
        """
        Get all Bank Transactions

        Returns:
            List of all transactions with pagination and generator
        """

        return list(self._get_all_generator(BankTransactions.GET_BANK_TRANSACTIONS, 'BankTransactions'))

    def get_by_id(self, bank_transaction_id):
        """
        Get bank transaction by bank_transaction_id

        Parameters:
            bank_transaction_id (str): Bank Transaction ID

        Returns:
            Bank Transaction dict
        """

        return self._get_request(
            BankTransactions.GET_BANK_TRANSACTION_BY_ID.format(bank_transaction_id)
        )

    def post(self, data):
        """
        Create new Bank Transaction

        Parameters:
            data (dict): Data to create bank transaction

        Returns:
             Response from API
        """

        return self._post_request(data, BankTransactions.POST_BANK_TRANSACTION)
