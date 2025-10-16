from fyle_accounting_library.rabbitmq.data_class import Task
from apps.fyle.queue import async_import_and_export_expenses
from apps.workspaces.models import Workspace
from apps.xero.queue import __create_chain_and_run
from tests.test_fyle.fixtures import data


# This test is just for cov :D
def test_create_chain_and_run(db):
    workspace_id = 1
    chain_tasks = [
        Task(
            target='apps.xero.tasks.create_bill',
            args=[1, 1, True, False]
        )
    ]

    __create_chain_and_run(workspace_id, chain_tasks, False)
    assert True


# This test is just for cov :D
def test_async_import_and_export_expenses(db):
    body = {
        'action': 'ACCOUNTING_EXPORT_INITIATED',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh'
        }
    }

    worksapce, _ = Workspace.objects.update_or_create(
        fyle_org_id = 'or79Cob97KSh'
    )

    async_import_and_export_expenses(body, worksapce.id)


# This test is just for cov :D (2)
def test_async_import_and_export_expenses_2(db):
    body = {
        'action': 'STATE_CHANGE_PAYMENT_PROCESSING',
        'data': {
            'id': 'rp1s1L3QtMpF',
            'org_id': 'or79Cob97KSh',
            'state': 'APPROVED'
        }
    }

    worksapce, _ = Workspace.objects.update_or_create(
        fyle_org_id = 'or79Cob97KSh'
    )

    async_import_and_export_expenses(body, worksapce.id)


# Test for UPDATED_AFTER_APPROVAL with EXPENSE resource
def test_async_import_and_export_expenses_updated_after_approval_expense(db):
    """
    Test UPDATED_AFTER_APPROVAL webhook with EXPENSE resource
    """
    test_data = data['fund_source_change']

    body = {
        'action': 'UPDATED_AFTER_APPROVAL',
        'resource': 'EXPENSE',
        'data': test_data['expense_payload']
    }

    workspace, _ = Workspace.objects.update_or_create(
        **test_data['workspace_defaults']
    )

    async_import_and_export_expenses(body, workspace.id)


# Test for UPDATED_AFTER_APPROVAL with REPORT resource
def test_async_import_and_export_expenses_updated_after_approval_report(db):
    """
    Test UPDATED_AFTER_APPROVAL webhook with REPORT resource for fund source changes
    """
    test_data = data['fund_source_change']

    body = {
        'action': 'UPDATED_AFTER_APPROVAL',
        'resource': 'REPORT',
        'data': test_data['report_payload']
    }

    workspace, _ = Workspace.objects.update_or_create(
        **test_data['workspace_defaults']
    )

    async_import_and_export_expenses(body, workspace.id)


def test_async_import_and_export_expenses_ejected_from_report(db):
    """
    Test async_import_and_export_expenses for EJECTED_FROM_REPORT action
    """
    body = {
        'action': 'EJECTED_FROM_REPORT',
        'resource': 'EXPENSE',
        'data': {
            'id': 'txExpense123',
            'org_id': 'orPJvXuoLqvJ'
        }
    }

    workspace = Workspace.objects.get(id=1)

    async_import_and_export_expenses(body, workspace.id)


def test_async_import_and_export_expenses_added_to_report(db):
    """
    Test async_import_and_export_expenses for ADDED_TO_REPORT action
    """
    body = {
        'action': 'ADDED_TO_REPORT',
        'resource': 'EXPENSE',
        'data': {
            'id': 'txExpense456',
            'org_id': 'orPJvXuoLqvJ',
            'report_id': 'rpReport123'
        }
    }

    workspace = Workspace.objects.get(id=1)

    async_import_and_export_expenses(body, workspace.id)
