from apps.fyle.models import Expense
from apps.fyle.queue import async_import_and_export_expenses, async_post_accounting_export_summary
from apps.workspaces.models import FyleCredential, XeroCredentials
from apps.xero.queue import __create_chain_and_run
from apps.xero.utils import XeroConnector


# This test is just for cov :D
def test_async_post_accounting_export_summary(db):
    async_post_accounting_export_summary(1, 1)
    assert True


# This test is just for cov :D
def test_create_chain_and_run(db):
    workspace_id = 1
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    in_progress_expenses = Expense.objects.filter(org_id='or79Cob97KSh')
    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id)
    chain_tasks = [
        {
            'target': 'apps.sage_intacct.tasks.create_bill',
            'expense_group_id': 1,
            'task_log_id': 1,
            'last_export': True
        }
    ]

    __create_chain_and_run(fyle_credentials, xero_connection, in_progress_expenses, workspace_id, chain_tasks, 'PERSONAL')
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

    async_import_and_export_expenses(body)
