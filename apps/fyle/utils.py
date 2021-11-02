from typing import List
import logging
import json

from django.conf import settings

from fylesdk import FyleSDK, UnauthorizedClientError, NotFoundClientError, InternalServerError, WrongParamsError

from fyle_accounting_mappings.models import ExpenseAttribute

import requests

from apps.fyle.models import Reimbursement

logger = logging.getLogger(__name__)

class FyleConnector:
    """
    Fyle utility functions
    """

    def __init__(self, refresh_token, workspace_id=None):
        client_id = settings.FYLE_CLIENT_ID
        client_secret = settings.FYLE_CLIENT_SECRET
        base_url = settings.FYLE_BASE_URL
        self.workspace_id = workspace_id

        self.connection = FyleSDK(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
        )

    def _post_request(self, url, body):
        """
        Create a HTTP post request.
        """

        access_token = self.connection.access_token
        api_headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer {0}'.format(access_token)
        }

        response = requests.post(
            url,
            headers=api_headers,
            data=body
        )

        if response.status_code == 200:
            return json.loads(response.text)

        elif response.status_code == 401:
            raise UnauthorizedClientError('Wrong client secret or/and refresh token', response.text)

        elif response.status_code == 404:
            raise NotFoundClientError('Client ID doesn\'t exist', response.text)

        elif response.status_code == 400:
            raise WrongParamsError('Some of the parameters were wrong', response.text)

        elif response.status_code == 500:
            raise InternalServerError('Internal server error', response.text)

    def _get_request(self, url, params):
        """
        Create a HTTP get request.
        """

        access_token = self.connection.access_token
        api_headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer {0}'.format(access_token)
        }
        api_params = {}

        for k in params:
            # ignore all unused params
            if not params[k] is None:
                p = params[k]

                # convert boolean to lowercase string
                if isinstance(p, bool):
                    p = str(p).lower()

                api_params[k] = p

        response = requests.get(
            url,
            headers=api_headers,
            params=api_params
        )

        if response.status_code == 200:
            return json.loads(response.text)

        elif response.status_code == 401:
            raise UnauthorizedClientError('Wrong client secret or/and refresh token', response.text)

        elif response.status_code == 404:
            raise NotFoundClientError('Client ID doesn\'t exist', response.text)

        elif response.status_code == 400:
            raise WrongParamsError('Some of the parameters were wrong', response.text)

        elif response.status_code == 500:
            raise InternalServerError('Internal server error', response.text)

    def get_employee_profile(self):
        """
        Get expenses from fyle
        """
        employee_profile = self.connection.Employees.get_my_profile()

        return employee_profile['data']

    def get_cluster_domain(self):
        """
        Get cluster domain name from fyle
        """

        body = {}
        api_url = '{0}/oauth/cluster/'.format(settings.FYLE_BASE_URL)

        return self._post_request(api_url, body)

    def get_fyle_orgs(self, cluster_domain):
        """
        Get fyle orgs of a user
        """

        params = {}
        api_url = '{0}/api/orgs/'.format(cluster_domain)

        return self._get_request(api_url, params)

    def get_expenses(self, state: List[str], updated_at: List[str], fund_source: List[str]):
        """
        Get expenses from fyle
        """
        expenses = self.connection.Expenses.get_all(state=state, updated_at=updated_at, fund_source=fund_source)
        expenses = list(filter(lambda expense: expense['amount'] > 0, expenses))
        expenses = list(
            filter(lambda expense: not (not expense['reimbursable'] and expense['fund_source'] == 'PERSONAL'),
                   expenses))

        return expenses

    def get_attachments(self, expense_ids: List[str]):
        """
        Get attachments against expense_ids
        """
        attachments = []
        if expense_ids:
            for expense_id in expense_ids:
                attachment_file_names = []
                attachment = self.connection.Expenses.get_attachments(expense_id)
                for attachment in attachment['data']:
                    if attachment['filename'] not in attachment_file_names:
                        attachment['expense_id'] = expense_id
                        attachments.append(attachment)
                        attachment_file_names.append(attachment['filename'])
            return attachments

        return []

    def sync_reimbursements(self):
        """
        Get reimbursements from fyle
        """
        reimbursements = self.connection.Reimbursements.get_all()

        Reimbursement.create_or_update_reimbursement_objects(
            reimbursements, self.workspace_id
        )

    def post_reimbursement(self, reimbursement_ids: list):
        """
        Process Reimbursements in bulk.
        """
        return self.connection.Reimbursements.post(reimbursement_ids)
