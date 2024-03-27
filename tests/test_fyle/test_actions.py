from unittest import mock

from django.conf import settings
from fyle.platform.exceptions import InternalServerError, RetryException, WrongParamsError
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.actions import (
    bulk_post_accounting_export_summary,
    create_generator_and_post_in_batches,
    mark_accounting_export_summary_as_synced,
    update_complete_expenses,
    update_expenses_in_progress,
    update_failed_expenses,
)
from apps.fyle.helpers import get_updated_accounting_export_summary
from apps.fyle.models import Expense
from apps.workspaces.models import FyleCredential


def test_update_expenses_in_progress(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    update_expenses_in_progress(expenses)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'IN_PROGRESS'
        assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
            settings.XERO_INTEGRATION_APP_URL
        )
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_update_failed_expenses(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    update_failed_expenses(expenses, True)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'ERROR'
        assert expense.accounting_export_summary['error_type'] == 'MAPPING'
        assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
            settings.XERO_INTEGRATION_APP_URL
        )
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_update_complete_expenses(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    update_complete_expenses(expenses, 'https://intacct.google.com')

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == False
        assert expense.accounting_export_summary['state'] == 'COMPLETE'
        assert expense.accounting_export_summary['error_type'] == None
        assert expense.accounting_export_summary['url'] == 'https://intacct.google.com'
        assert expense.accounting_export_summary['id'] == expense.expense_id


def test_create_generator_and_post_in_batches(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=1)
    platform = PlatformConnector(fyle_credentails)

    with mock.patch('fyle.platform.apis.v1beta.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = RetryException('Timeout')
        try:
            create_generator_and_post_in_batches([{
                'id': 'txxTi9ZfdepC'
            }], platform, 1)

            # Exception should be handled
            assert True
        except RetryException:
            # This should not be reached
            assert False


def test_handle_post_accounting_export_summary_exception(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=1)
    platform = PlatformConnector(fyle_credentails)
    expense = Expense.objects.filter(org_id='orPJvXuoLqvJ').first()
    expense.workspace_id = 1
    expense.save()

    expense_id = expense.expense_id

    with mock.patch('fyle.platform.apis.v1beta.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = WrongParamsError('Some of the parameters are wrong', {
            'data': [
                {
                    'message': 'Permission denied to perform this action.',
                    'key': expense_id
                }
            ]
        })
        create_generator_and_post_in_batches([{
            'id': expense_id
        }], platform, 1)

    expense = Expense.objects.get(expense_id=expense_id)

    assert expense.accounting_export_summary['synced'] == True
    assert expense.accounting_export_summary['state'] == 'DELETED'
    assert expense.accounting_export_summary['error_type'] == None
    assert expense.accounting_export_summary['url'] == '{}/main/dashboard'.format(
        settings.XERO_INTEGRATION_APP_URL
    )
    assert expense.accounting_export_summary['id'] == expense_id


def test_mark_accounting_export_summary_as_synced(db):
    expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    for expense in expenses:
        expense.accounting_export_summary = get_updated_accounting_export_summary(
            'tx_123',
            'SKIPPED',
            None,
            '{}/main/export_log'.format(settings.XERO_INTEGRATION_APP_URL),
            True
        )
        expense.save()

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    mark_accounting_export_summary_as_synced(expenses)

    expenses = Expense.objects.filter(org_id='or79Cob97KSh')

    for expense in expenses:
        assert expense.accounting_export_summary['synced'] == True


def test_bulk_post_accounting_export_summary(db):
    fyle_credentails = FyleCredential.objects.get(workspace_id=1)
    platform = PlatformConnector(fyle_credentails)

    with mock.patch('fyle.platform.apis.v1beta.admin.Expenses.post_bulk_accounting_export_summary') as mock_call:
        mock_call.side_effect = InternalServerError('Timeout')
        try:
            bulk_post_accounting_export_summary(platform, {})
        except RetryException:
            assert mock_call.call_count == 3
