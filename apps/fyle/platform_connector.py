import logging
from django.conf import settings

from fyle.platform import Platform

from apps.workspaces.models import FyleCredential

from .helpers import store_cluster_domain

logger = logging.getLogger(__name__)
logger.level = logging.INFO

class PlatformConnector:
    """
    Platform connector
    """

    def __init__(self, fyle_credentials: FyleCredential, workspace_id=None):
        """
        Initialize the Fyle platform connector
        """
        if not fyle_credentials.cluster_domain:
            fyle_credentials = store_cluster_domain(fyle_credentials)

        server_url = '{}/platform/v1'.format(fyle_credentials.cluster_domain)
        self.workspace_id = workspace_id

        self.connection = Platform(
            server_url=server_url,
            token_url=settings.FYLE_TOKEN_URI,
            client_id=settings.FYLE_CLIENT_ID,
            client_secret=settings.FYLE_CLIENT_SECRET,
            refresh_token=fyle_credentials.refresh_token
        )

    def get_expenses(self, state: str, updated_at: str, fund_source: str):
        """
        Get expenses from fyle
        """
        expenses = []
        query_params = {
            'order': 'updated_at.desc',
            'source_account->type': fund_source,
            'state': state
        }
        # When last_synced_at is null (For new orgs)
        if updated_at:
            query_params['updated_at'] = updated_at

        logger.info('query_params {}'.format(query_params))
        generator = self.connection.v1.admin.expenses.list_all(query_params)

        for expense_list in generator:
            debit_expenses = list(filter(lambda expense: expense['amount'] > 0, expense_list['data']))
            debit_expenses = list(
                filter(
                    lambda expense: not (
                        not expense['is_reimbursable'] and expense['source_account']['type'] == 'PERSONAL_CASH_ACCOUNT'
                    ),
                    debit_expenses
                )
            )
            expenses.extend(debit_expenses)

        return expenses
