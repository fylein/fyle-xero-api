import json
import logging
import traceback
from typing import List, Union

import django_filters
import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings

logger = logging.getLogger(__name__)

SOURCE_ACCOUNT_MAP = {'PERSONAL': 'PERSONAL_CASH_ACCOUNT', 'CCC': 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'}


def post_request(url, body, refresh_token=None):
    """
    Create a HTTP post request.
    """
    access_token = None
    api_headers = {
        'content-type': 'application/json'
    }
    if refresh_token:
        access_token = get_access_token(refresh_token)

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


def get_updated_accounting_export_summary(
        expense_id: str, state: str, error_type: Union[str, None], url: Union[str, None], is_synced: bool) -> dict:
    """
    Get updated accounting export summary
    :param expense_id: expense id
    :param state: state
    :param error_type: error type
    :param url: url
    :param is_synced: is synced
    :return: updated accounting export summary
    """
    return {
        'id': expense_id,
        'state': state,
        'error_type': error_type,
        'url': url,
        'synced': is_synced
    }


def get_batched_expenses(batched_payload: List[dict], workspace_id: int) -> List[Expense]:
    """
    Get batched expenses
    :param batched_payload: batched payload
    :param workspace_id: workspace id
    :return: batched expenses
    """
    expense_ids = [expense['id'] for expense in batched_payload]
    return Expense.objects.filter(expense_id__in=expense_ids, workspace_id=workspace_id)


def assert_valid_request(workspace_id:int, fyle_org_id:str):
    """
    Assert if the request is valid by checking
    the url_workspace_id and fyle_org_id workspace
    """
    workspace = Workspace.objects.get(fyle_org_id=fyle_org_id)
    if workspace.id != workspace_id:
        raise ValidationError('Workspace mismatch')


class AdvanceSearchFilter(django_filters.FilterSet):
    def filter_queryset(self, queryset):
        or_filtered_queryset = queryset.none()
        or_filter_fields = getattr(self.Meta, 'or_fields', [])
        or_field_present = False

        for field_name in self.Meta.fields:
            value = self.data.get(field_name)
            if value:
                if field_name == 'is_skipped':
                    value = True if str(value) == 'true' else False
                filter_instance = self.filters[field_name]
                queryset = filter_instance.filter(queryset, value)

        for field_name in or_filter_fields:
            value = self.data.get(field_name)
            if value:
                or_field_present = True
                filter_instance = self.filters[field_name]
                field_filtered_queryset = filter_instance.filter(queryset, value)
                or_filtered_queryset |= field_filtered_queryset

        if or_field_present:
            queryset = queryset & or_filtered_queryset
            return queryset

        return queryset


class ExpenseGroupSearchFilter(AdvanceSearchFilter):
    exported_at__gte = django_filters.DateTimeFilter(lookup_expr='gte', field_name='exported_at')
    exported_at__lte = django_filters.DateTimeFilter(lookup_expr='lte', field_name='exported_at')
    tasklog__status = django_filters.CharFilter()
    expenses__expense_number = django_filters.CharFilter(field_name='expenses__expense_number', lookup_expr='icontains')
    expenses__employee_name = django_filters.CharFilter(field_name='expenses__employee_name', lookup_expr='icontains')
    expenses__employee_email = django_filters.CharFilter(field_name='expenses__employee_email', lookup_expr='icontains')
    expenses__claim_number = django_filters.CharFilter(field_name='expenses__claim_number', lookup_expr='icontains')

    class Meta:
        model = ExpenseGroup
        fields = ['exported_at__gte', 'exported_at__lte', 'tasklog__status']
        or_fields = ['expenses__expense_number', 'expenses__employee_name', 'expenses__employee_email', 'expenses__claim_number']
