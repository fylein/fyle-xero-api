import json
import traceback
import logging
from typing import List

import requests
from django.conf import settings
from apps.fyle.models import ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings

logger = logging.getLogger(__name__)

SOURCE_ACCOUNT_MAP = {'PERSONAL': 'PERSONAL_CASH_ACCOUNT', 'CCC': 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'}


def post_request(url, body, refresh_token=None):
    """
    Create a HTTP post request.
    """
    access_token = None
    api_headers = {}
    if refresh_token:
        access_token = get_access_token(refresh_token)

        api_headers["content-type"] = "application/json"
        api_headers["Authorization"] = "Bearer {0}".format(access_token)

    response = requests.post(url, headers=api_headers, data=body)

    if response.status_code in [200, 201]:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_source_account_type(fund_source: List[str]) -> List[str]:
    """
    Get source account type
    :param fund_source: fund source
    :return: source account type
    """
    source_account_type = []
    for source in fund_source:
        source_account_type.append(SOURCE_ACCOUNT_MAP[source])

    return source_account_type


def get_filter_credit_expenses(expense_group_settings: ExpenseGroupSettings) -> bool:
    """
    Get filter credit expenses
    :param expense_group_settings: expense group settings
    :return: filter credit expenses
    """
    filter_credit_expenses = True
    if expense_group_settings.import_card_credits:
        filter_credit_expenses = False

    return filter_credit_expenses


def get_fund_source(workspace_id: int) -> List[str]:
    """
    Get fund source
    :param workspace_id: workspace id
    :return: fund source
    """
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if general_settings.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    return fund_source


def handle_import_exception(task_log: TaskLog) -> None:
    """
    Handle import exception
    :param task_log: task log
    :return: None
    """
    error = traceback.format_exc()
    task_log.detail = {'error': error}
    task_log.status = 'FATAL'
    task_log.save()
    logger.error('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def get_request(url, params, refresh_token):
    """
    Create a HTTP get request.
    """
    access_token = get_access_token(refresh_token)
    api_headers = {
        "content-type": "application/json",
        "Authorization": "Bearer {0}".format(access_token),
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

    response = requests.get(url, headers=api_headers, params=api_params)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(response.text)


def get_access_token(refresh_token: str) -> str:
    """
    Get access token from fyle
    """
    api_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.FYLE_CLIENT_ID,
        "client_secret": settings.FYLE_CLIENT_SECRET,
    }

    return post_request(settings.FYLE_TOKEN_URI, body=api_data)["access_token"]


def get_fyle_orgs(refresh_token: str, cluster_domain: str):
    """
    Get fyle orgs of a user
    """
    api_url = "{0}/api/orgs/".format(cluster_domain)

    return get_request(api_url, {}, refresh_token)


def get_cluster_domain(refresh_token: str) -> str:
    """
    Get cluster domain name from fyle
    :param refresh_token: (str)
    :return: cluster_domain (str)
    """
    cluster_api_url = "{0}/oauth/cluster/".format(settings.FYLE_BASE_URL)

    return post_request(cluster_api_url, {}, refresh_token)["cluster_domain"]
