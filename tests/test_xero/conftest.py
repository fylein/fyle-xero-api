from datetime import datetime

import pytest

from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.workspaces.models import LastExportDetail, WorkspaceGeneralSettings
from apps.xero.models import BankTransaction, BankTransactionLineItem, Bill, BillLineItem


@pytest.fixture
def create_bill(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=4)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(
        workspace_id=workspace_id
    )
    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineItem.create_bill_lineitems(
        expense_group, workspace_general_settings
    )

    return bill, bill_lineitems


@pytest.fixture
def create_bank_transaction(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=5)
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(
        workspace_id=workspace_id
    )
    bank_transaction = BankTransaction.create_bank_transaction(expense_group, True)
    bank_transaction_lineitems = (
        BankTransactionLineItem.create_bank_transaction_lineitems(
            expense_group, workspace_general_settings
        )
    )

    return bank_transaction, bank_transaction_lineitems


@pytest.fixture
def create_task_logs(db):
    TaskLog.objects.update_or_create(
        workspace_id=1, type="FETCHING_EXPENSES", defaults={"status": "READY"}
    )


@pytest.fixture
def create_last_export_detail(db):
    LastExportDetail.objects.create(
        workspace_id=1,
        export_mode='MANUAL',
        total_expense_groups_count=2,
        successful_expense_groups_count=0,
        failed_expense_groups_count=0,
        last_exported_at=datetime.now(),
    )
