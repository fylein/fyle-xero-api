
import ast
import os
import logging
import pytest
from apps.xero.utils import XeroConnector, XeroCredentials

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_token_health():
    refresh_tokens = ast.literal_eval(os.environ.get('XERO_TESTS_REFRESH_TOKENS'))
    num_token_expired = 0

    for workspace_id in refresh_tokens.keys():
        try:
            xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
            xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)
            xero_connection.get_organisations()
            logger.info('xero_connection succeded - %s', xero_connection)

        except Exception as error:
            num_token_expired += 1
            logger.info('error for workspace id - %s', workspace_id)
            logger.info('Error message - %s', error)

    logger.info('refresh tokens - %s', ast.literal_eval(os.environ.get('XERO_TESTS_REFRESH_TOKENS')))

    if num_token_expired != 0:
        pytest.exit("Refresh token expired")
