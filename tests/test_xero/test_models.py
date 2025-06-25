from datetime import datetime

from fyle_accounting_mappings.models import Mapping, MappingSetting

from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.xero.models import (
    BankTransaction,
    BankTransactionLineItem,
    Bill,
    BillLineItem,
    Payment,
    get_customer_id_or_none,
    get_expense_purpose,
    get_item_code_or_none,
    get_tax_code_id_or_none,
    get_tracking_category,
    get_transaction_date,
)
from apps.xero.tasks import create_bank_transaction
from tests.test_fyle.fixtures import data
from tests.test_xero.fixtures import data as xero_data


def test_create_bill(db):
    expense_group = ExpenseGroup.objects.get(id=4)
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=expense_group.workspace_id).first()

    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineItem.create_bill_lineitems(expense_group, workspace_general_settings)

    for bill_lineitem in bill_lineitems:
        assert bill_lineitem.amount == 10.0
        assert (
            bill_lineitem.description
            == "sravan.kumar@fyle.in - Food -  - 2020-01-01 - C/2022/06/R/1 - "
        )

    assert bill.currency == "USD"


def test_bank_transaction(db):
    expense_group = ExpenseGroup.objects.get(id=5)
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=expense_group.workspace_id).first()

    bank_transaction = BankTransaction.create_bank_transaction(expense_group, True)
    bank_transaction_lineitems = (
        BankTransactionLineItem.create_bank_transaction_lineitems(expense_group, workspace_general_settings)
    )

    for bank_transaction_lineitem in bank_transaction_lineitems:
        assert bank_transaction_lineitem.amount == 101.0

    assert bank_transaction.currency == "USD"
    assert bank_transaction.transaction_date == "2022-05-24"


def test_create_payment(db):
    expense_group = ExpenseGroup.objects.get(id=7)

    payment = Payment.create_payment(
        expense_group=expense_group, invoice_id="sdfgh", account_id="sdfgh"
    )

    assert payment.amount == 45.0
    assert payment.invoice_id == "sdfgh"


def test_get_tracking_category(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        tracking_categories = get_tracking_category(expense_group, lineitem)
        assert tracking_categories == []


def test_get_item_code_or_none(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    mapping_setting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id,
    ).first()

    mapping_setting.destination_field = "ITEM"
    mapping_setting.save()

    for lineitem in expenses:
        item_code = get_item_code_or_none(expense_group, lineitem)
        assert item_code == None

    mapping_setting.source_field = "PROJECT"
    mapping_setting.save()

    mapping = Mapping.objects.filter(
        source_type="PROJECT",
        workspace_id=expense_group.workspace_id,
    ).first()

    mapping.destination_type = "ITEM"
    mapping.save()

    for lineitem in expenses:
        lineitem.project = "Bank West"
        item_code = get_item_code_or_none(expense_group, lineitem)
        assert item_code == "Bank West"

    mapping_setting.source_field = "COST_CENTER"
    mapping_setting.save()

    for lineitem in expenses:
        lineitem.cost_center = "Adidas"
        item_code = get_item_code_or_none(expense_group, lineitem)
        assert item_code == None


def test_get_tax_code_id_or_none(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        tax_code = get_tax_code_id_or_none(expense_group, lineitem)
        assert tax_code == None


def test_get_customer_id_or_none(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        lineitem.billable = True
        lineitem.project = "Bank West"
        bill_lineitem_objects = get_customer_id_or_none(expense_group, lineitem)
        assert bill_lineitem_objects == "47f61ab1-5245-40a2-a3a5-bc224c850c8d"

    mapping_setting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id, destination_field="CUSTOMER"
    ).first()
    mapping_setting.source_field = "PROJECT"
    mapping_setting.save()

    for lineitem in expenses:
        bill_lineitem_objects = get_customer_id_or_none(expense_group, lineitem)
        assert bill_lineitem_objects == "47f61ab1-5245-40a2-a3a5-bc224c850c8d"

    mapping_setting.source_field = "COST_CENTER"
    mapping_setting.save()
    for lineitem in expenses:
        bill_lineitem_objects = get_customer_id_or_none(expense_group, lineitem)
        assert bill_lineitem_objects == None


def test_get_expense_purpose(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=10)
    expenses = expense_group.expenses.all()

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

    for lineitem in expenses:
        category = (
            lineitem.category
            if lineitem.category == lineitem.sub_category
            else "{0} / {1}".format(lineitem.category, lineitem.sub_category)
        )

        expense_purpose = get_expense_purpose(workspace_id, lineitem, category, workspace_general_settings)

        assert (
            expense_purpose
            == "sravan.kumar@fyle.in - WIP / None -  - 2022-05-25 - C/2022/05/R/13 - "
        )


def test_get_transaction_date(db):
    expense_group = ExpenseGroup.objects.get(id=8)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime("%Y-%m-%d")

    expense_group.description.pop("spent_at")

    approved_at = {"approved_at": "2000-09-14"}
    expense_group.description.update(approved_at)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime("%Y-%m-%d")

    verified_at = {"verified_at": "2000-09-14"}
    expense_group.description.pop("approved_at")
    expense_group.description.update(verified_at)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime("%Y-%m-%d")

    last_spent_at = {"last_spent_at": "2000-09-14"}
    expense_group.description.pop("verified_at")
    expense_group.description.update(last_spent_at)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime("%Y-%m-%d")


def test_support_post_date_integrations(mocker, db):
    workspace_id = 1
    payload = data["expenses"]
    expense_id = data["expenses"][0]["id"]
    Expense.create_expense_objects(payload, workspace_id)
    expense_objects = Expense.objects.get(expense_id=expense_id)
    expense_objects.reimbursable = False
    expense_objects.fund_source = "CCC"
    expense_objects.source_account_type = "PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT"
    expense_objects.save()
    assert expense_objects.posted_at.strftime("%m/%d/%Y") == "12/22/2021"

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.reimbursable_export_date_type = "last_spent_at"
    expense_group_settings.ccc_export_date_type = "posted_at"
    expense_group_settings.corporate_credit_card_expense_group_fields = [
        "claim_number",
        "fund_source",
        "projects",
        "employee_email",
        "report_id",
        "posted_at",
    ]
    expense_group_settings.save()

    expense_groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        [expense_objects], workspace_id
    )
    assert expense_groups[0].description[
        "posted_at"
    ] == expense_objects.posted_at.strftime("%Y-%m-%d")

    mocker.patch(
        "xerosdk.apis.BankTransactions.post",
        return_value=xero_data["bank_transaction_object"],
    )

    mocker.patch(
        "xerosdk.apis.Contacts.search_contact_by_contact_name",
        return_value=xero_data["create_contact"]["Contacts"][0],
    )

    mocker.patch(
        "xerosdk.apis.Contacts.post",
        return_vaue=xero_data["create_contact"]["Contacts"][0],
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=1)

    general_settings.auto_map_employees = "NAME"
    general_settings.import_items = False
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    task_log = TaskLog.objects.first()
    task_log.workspace_id = 1
    task_log.status = "READY"
    task_log.type = "CREATING_BANK_TRANSACTION"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=5)
    expense_group.description.pop("spent_at")
    expense_group.description["posted_at"] = "2021-12-22"
    expense_group.save()
    expenses = expense_group.expenses.all()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

        bank_transaction_lineitems = BankTransactionLineItem.objects.get(
            expense_id=expense.id
        )
        bank_transaction_lineitems.delete()

    expense_group.expenses.set(expenses)

    create_bank_transaction(expense_group.id, task_log.id, False, False)

    task_log = TaskLog.objects.get(pk=task_log.id)
    bank_transaction = BankTransaction.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == "COMPLETE"
    assert bank_transaction.currency == "USD"
    assert bank_transaction.transaction_date.strftime(
        "%m/%d/%Y"
    ) == expense_objects.posted_at.strftime("%m/%d/%Y")
