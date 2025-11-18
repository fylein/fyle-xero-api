from asyncio.log import logger

import pytest
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.actions import __bulk_update_expenses
from apps.fyle.helpers import assert_valid_request, get_request, get_updated_accounting_export_summary, post_request
from apps.fyle.models import Expense
from apps.workspaces.models import Workspace


def test_post_request(mocker):
    mocker.patch(
        "apps.fyle.helpers.requests.post",
        return_value=Response({"message": "Post request"}, status=status.HTTP_200_OK),
    )
    try:
        post_request(url="sdfghjk", body={}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")

    mocker.patch(
        "apps.fyle.helpers.requests.post",
        return_value=Response(
            {"message": "Post request"}, status=status.HTTP_400_BAD_REQUEST
        ),
    )
    try:
        post_request(url="sdfghjk", body={}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")


def test_get_request(mocker):
    mocker.patch(
        "apps.fyle.helpers.requests.get",
        return_value=Response({"message": "Get request"}, status=status.HTTP_200_OK),
    )
    try:
        get_request(url="sdfghjk", params={"key": "sample"}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")

    mocker.patch(
        "apps.fyle.helpers.requests.get",
        return_value=Response(
            {"message": "Get request"}, status=status.HTTP_400_BAD_REQUEST
        ),
    )
    try:
        get_request(url="sdfghjk", params={"sample": True}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")


def test_bulk_update_expenses(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    for expense in expenses:
        expense.accounting_export_summary = get_updated_accounting_export_summary(
            expense.expense_id,
            'SKIPPED',
            None,
            '{}/main/export_log'.format(settings.XERO_INTEGRATION_APP_URL),
            True
        )
        expense.save()

    __bulk_update_expenses(expenses)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == True
        assert expense.accounting_export_summary['state'] == 'SKIPPED'
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['url'] == '{}/main/export_log'.format(
            settings.XERO_INTEGRATION_APP_URL
        )
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_assert_valid_request_with_cache(db, mocker):
    workspace = Workspace.objects.get(id=1)

    mock_cache_get = mocker.patch('apps.fyle.helpers.cache.get', return_value=None)
    mock_cache_set = mocker.patch('apps.fyle.helpers.cache.set')

    assert_valid_request(workspace_id=workspace.id, fyle_org_id=workspace.fyle_org_id)

    mock_cache_get.assert_called_once()
    mock_cache_set.assert_called_once()

    mock_cache_get.return_value = True
    assert_valid_request(workspace_id=workspace.id, fyle_org_id=workspace.fyle_org_id)

    assert mock_cache_get.call_count == 2
    assert mock_cache_set.call_count == 1


def test_assert_valid_request_invalid(db):
    with pytest.raises(ValidationError, match='Workspace not found'):
        assert_valid_request(workspace_id=99999, fyle_org_id='invalid_org')


def test_assert_valid_request_mismatch(db):
    workspace = Workspace.objects.get(id=1)

    with pytest.raises(ValidationError, match='Workspace mismatch'):
        assert_valid_request(workspace_id=999, fyle_org_id=workspace.fyle_org_id)
