from asyncio.log import logger

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.actions import __bulk_update_expenses
from apps.fyle.helpers import get_fyle_orgs, get_request, get_updated_accounting_export_summary, post_request
from apps.fyle.models import Expense


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


def test_get_fyle_orgs(mocker):
    mocker.patch(
        "apps.fyle.helpers.requests.get",
        return_value=Response({"message": "Get request"}, status=status.HTTP_200_OK),
    )
    try:
        get_fyle_orgs(refresh_token="srtyu", cluster_domain="erty")
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
