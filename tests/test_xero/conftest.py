import pytest
from apps.fyle.models import Expense, ExpenseGroup
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem, Payment
from apps.tasks.models import TaskLog


@pytest.fixture
def create_bill(db):
    expense_group = ExpenseGroup.objects.get(id=4)

    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineItem.create_bill_lineitems(expense_group)

    return bill, bill_lineitems


@pytest.fixture
def create_bank_transaction(db):
    expense_group = ExpenseGroup.objects.get(id=5)
    
    bank_transaction = BankTransaction.create_bank_transaction(expense_group, True)
    bank_transaction_lineitems  = BankTransactionLineItem.create_bank_transaction_lineitems(expense_group)

    return bank_transaction,bank_transaction_lineitems


@pytest.fixture
def create_task_logs(db):
    TaskLog.objects.update_or_create(
        workspace_id=1,
        type='FETCHING_EXPENSES',
        defaults={
            'status': 'READY'
        }
    )
