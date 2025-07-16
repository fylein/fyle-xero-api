import logging
import random
from datetime import datetime, timedelta, timezone
from unittest import mock

from django_q.models import Schedule
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_mappings.models import ExpenseAttribute, Mapping
from xerosdk.exceptions import InvalidGrant, NoPrivilegeError, RateLimitError, WrongParamsError, XeroSDKError

from apps.fyle.models import Expense, ExpenseGroup, Reimbursement
from apps.mappings.models import GeneralMapping, TenantMapping
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import LastExportDetail, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.exceptions import update_last_export_details
from apps.xero.models import BankTransaction, BankTransactionLineItem, Bill, BillLineItem
from apps.xero.queue import (
    handle_skipped_exports,
    schedule_bank_transaction_creation,
    schedule_bills_creation,
    schedule_payment_creation,
    schedule_reimbursements_sync,
    schedule_xero_objects_status_sync,
)
from apps.xero.tasks import (
    __validate_expense_group,
    attach_customer_to_export,
    check_xero_object_status,
    create_bank_transaction,
    create_bill,
    create_missing_currency,
    create_or_update_employee_mapping,
    create_payment,
    get_or_create_credit_card_contact,
    load_attachments,
    process_reimbursements,
    update_xero_short_code,
)
from apps.xero.utils import XeroConnector
from fyle_xero_api.exceptions import BulkError
from tests.test_fyle.fixtures import data as fyle_data
from tests.test_xero.fixtures import data
from tests.test_xero.fixtures import data as xero_data

logger = logging.getLogger(__name__)


def test_get_or_create_credit_card_contact(mocker, db):
    mocker.patch("apps.xero.utils.XeroConnector.get_or_create_contact", return_value=[])
    workspace_id = 1

    contact = get_or_create_credit_card_contact(workspace_id, "samp_merchant", False)
    assert contact == []

    contact = get_or_create_credit_card_contact(workspace_id, "samp_merchant", True)
    assert contact == []

    try:
        with mock.patch(
            "apps.xero.utils.XeroConnector.get_or_create_contact"
        ) as mock_call:
            mock_call.side_effect = [
                None,
                WrongParamsError(msg="wrong parameters", response="wrong parameters"),
            ]
            contact = get_or_create_credit_card_contact(
                workspace_id, "samp_merchant", False
            )
    except Exception:
        logger.info("wrong parameters")

    contact = get_or_create_credit_card_contact(workspace_id, "", True)
    assert contact == []

    mocker.patch(
        "apps.xero.utils.XeroConnector.get_or_create_contact",
        return_value={"name": "Books by Bessie"},
    )

    contact = get_or_create_credit_card_contact(workspace_id, "Books by Bessie", True)
    assert contact == {"name": "Books by Bessie"}

    try:
        with mock.patch(
            "apps.xero.utils.XeroConnector.get_or_create_contact"
        ) as mock_call:
            mock_call.side_effect = WrongParamsError(
                msg="wrong parameters", response="wrong parameters"
            )
            contact = get_or_create_credit_card_contact(
                workspace_id, "samp_merchant", False
            )
    except Exception:
        logger.info("wrong parameters")


def test_load_attachments(mocker, db):
    mocker.patch(
        "fyle_integrations_platform_connector.apis.Files.bulk_generate_file_urls",
        return_value=[],
    )
    mocker.patch(
        "apps.xero.utils.XeroConnector.post_attachments",
        return_value=[],
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(
        credentials_object=xero_credentials, workspace_id=workspace_id
    )

    expense_group = ExpenseGroup.objects.get(id=4)
    expenses = expense_group.expenses.all()

    for expense in expenses:
        expense.file_ids = ["asdfghj"]
        expense.save()

    load_attachments(xero_connection, "dfgh", "werty", expense_group)

    with mock.patch("apps.xero.utils.XeroConnector.post_attachments") as mock_call:
        mock_call.side_effect = Exception()
        load_attachments(xero_connection, "dfgh", "werty", expense_group)


def test_attach_customer_to_export(mocker, db):
    mocker.patch(
        "xerosdk.apis.LinkedTransactions.post",
        return_value=[],
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(
        credentials_object=xero_credentials, workspace_id=workspace_id
    )

    bill = Bill.objects.filter(id=4).first()
    bill_lineitems = BillLineItem.objects.get(bill_id=bill.id)
    bill_lineitems.customer_id = "234"
    bill_lineitems.save()

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.type = "CREATING_BILL"
    task_log.bill = bill
    task_log.save()

    attach_customer_to_export(xero_connection, task_log)

    try:
        with mock.patch("xerosdk.apis.LinkedTransactions.post") as mock_call:
            mock_call.side_effect = Exception()
            attach_customer_to_export(xero_connection, task_log)
        assert 1 == 2
    except Exception:
        logger.info("Something unexpected happened during attaching customer to export")


def test_create_or_update_employee_mapping(mocker, db):
    workspace_id = 1

    mocker.patch(
        "xerosdk.apis.Contacts.search_contact_by_contact_name",
        return_value=data["create_contact"]["Contacts"][0],
    )

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(
        credentials_object=xero_credentials, workspace_id=workspace_id
    )

    expense_group = ExpenseGroup.objects.get(id=4)
    expense_group.description.update({"employee_email": "ironman@fyle.in"})
    expense_group.save()

    source = ExpenseAttribute.objects.get(
        attribute_type="EMPLOYEE",
        value__iexact="ironman@fyle.in",
        workspace_id=workspace_id,
    )
    mapping = Mapping.objects.filter(source=source)
    mapping.delete()

    create_or_update_employee_mapping(
        expense_group=expense_group,
        xero_connection=xero_connection,
        auto_map_employees_preference="EMAIL",
    )

    with mock.patch(
        "fyle_accounting_mappings.models.Mapping.create_or_update_mapping"
    ) as mock_call:
        mapping = Mapping.objects.filter(source=source)
        mapping.delete()

        mock_call.side_effect = WrongParamsError(
            msg="wrong parameters", response="wrong parameters"
        )
        create_or_update_employee_mapping(
            expense_group=expense_group,
            xero_connection=xero_connection,
            auto_map_employees_preference="NAME",
        )


def test_create_bill_early_return(mocker, create_task_logs, db):
    """
    Test create_bill function returns early when task log is already in progress/complete
    """
    workspace_id = 1
    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "IN_PROGRESS"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=4)
    create_bill(expense_group.id, task_log.id, False, False)

    # Verify task log status remains unchanged
    task_log.refresh_from_db()
    assert task_log.status == "IN_PROGRESS"


def test_create_bank_transaction_early_return(mocker, create_task_logs, db):
    """
    Test create_bank_transaction function returns early when task log is already in progress/complete
    """
    workspace_id = 1
    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "COMPLETE"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=3)
    create_bank_transaction(expense_group.id, task_log.id, False, False)

    # Verify task log status remains unchanged
    task_log.refresh_from_db()
    assert task_log.status == "COMPLETE"


def test_post_bill_success(mocker, create_task_logs, db):
    mocker.patch("xerosdk.apis.Invoices.post", return_value=data["bill_object"])
    workspace_id = 1

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.type = "CREATING_BILL"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=4)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

        bill_lineitems = BillLineItem.objects.get(expense_id=expense.id)
        bill_lineitems.delete()

    expense_group.expenses.set(expenses)

    create_bill(expense_group.id, task_log.id, False, False)

    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == "COMPLETE"
    assert bill.currency == "USD"

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.type = "CREATING_BILL"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=3)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

        bill_lineitems = BillLineItem.objects.get(expense_id=expense.id)
        bill_lineitems.delete()

    expense_group.expenses.set(expenses)

    create_bill(expense_group.id, task_log.id, False, False)

    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)

    assert task_log.status == "COMPLETE"
    assert bill.currency == "USD"


def test_create_bill_exceptions(db):
    workspace_id = 1

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.type = "CREATING_BILL"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=4)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

        bill_lineitems = BillLineItem.objects.get(expense_id=expense.id)
        bill_lineitems.delete()

    expense_group.expenses.set(expenses)

    with mock.patch("apps.xero.utils.XeroConnector.post_bill") as mock_call:
        mock_call.side_effect = XeroCredentials.DoesNotExist()
        create_bill(expense_group.id, task_log.id, False, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == "FAILED"

        mock_call.side_effect = BulkError(
            msg="employess not found", response="mapping error"
        )
        create_bill(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = InvalidGrant(
            msg="invalid grant", response="invalid grant"
        )
        create_bill(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = RateLimitError(
            msg="rate limit exceeded", response="rate limit exceeded"
        )
        create_bill(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = NoPrivilegeError(
            msg="no privilage error", response="no privilage error"
        )
        create_bill(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = XeroSDKError(
            msg="wrong parameter", response="xerosdk error"
        )
        create_bill(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = WrongParamsError(
            msg={"Message": "Invalid parametrs"}, response="Invalid params"
        )
        create_bill(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = WrongParamsError(
            {
                "ErrorNumber": 10,
                "Type": "ValidationException",
                "Message": "A validation exception occurred",
                "Elements": [
                    {
                        "BankAccount": {
                            "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4",
                            "Code": "090",
                            "ValidationErrors": [],
                        },
                        "Type": "SPEND",
                        "Reference": "E/2022/03/T/1",
                        "Url": "None/app/admin/#/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn",
                        "IsReconciled": False,
                        "Contact": {
                            "ContactID": "73e6b7fb-ba7e-4b0a-a08b-f971b8ebbed8",
                            "Addresses": [],
                            "Phones": [],
                            "ContactGroups": [],
                            "ContactPersons": [],
                            "HasValidationErrors": False,
                            "ValidationErrors": [],
                        },
                        "DateString": "2022-03-30T00:00:00",
                        "Date": "/Date(1648598400000+0000)/",
                        "Status": "AUTHORISED",
                        "LineAmountTypes": "Exclusive",
                        "LineItems": [
                            {
                                "Description": "ashwin.t@fyle.in, category - Food spent on 2022-03-30, report number - C/2022/03/R/1  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn",
                                "UnitAmount": 92.38,
                                "TaxType": "OUTPUT",
                                "TaxAmount": 7.62,
                                "LineAmount": 92.38,
                                "AccountCode": "425",
                                "Tracking": [],
                                "Quantity": 1.0,
                                "AccountID": "c4b1c463-9913-4672-a8b8-01a3b546126f",
                                "ValidationErrors": [],
                            }
                        ],
                        "SubTotal": 92.38,
                        "TotalTax": 7.62,
                        "Total": 100.0,
                        "CurrencyCode": "USD",
                        "ValidationErrors": [
                            {"Message": "Url must be a valid absolute url"}
                        ],
                    }
                ],
            }
        )
        create_bill(expense_group.id, task_log.id, False, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == "FAILED"


def test_schedule_bills_creation(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=4)
    expense_group.exported_at = None
    expense_group.save()

    bill = Bill.objects.filter(expense_group_id=expense_group.id).first()
    bill.expense_group_id = 5
    bill.save()

    task_log = TaskLog.objects.filter(bill_id=bill.id).first()
    task_log.status = "READY"
    task_log.save()

    schedule_bills_creation(
        workspace_id=workspace_id, expense_group_ids=[4], is_auto_export=False, interval_hours=0, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False
    )


def test_post_create_bank_transaction_success(mocker, db):
    mocker.patch(
        "xerosdk.apis.BankTransactions.post",
        return_value=data["bank_transaction_object"],
    )

    mocker.patch(
        "xerosdk.apis.Contacts.search_contact_by_contact_name",
        return_value=data["create_contact"]["Contacts"][0],
    )

    mocker.patch(
        "xerosdk.apis.Contacts.post", return_vaue=data["create_contact"]["Contacts"][0]
    )
    workspace_id = 1

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.type = "CREATING_BANK_TRANSACTION"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=5)
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

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.type = "CREATING_BANK_TRANSACTION"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=6)
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


def test_schedule_bank_transaction_creation(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=5)
    expense_group.exported_at = None
    expense_group.save()

    bank_transaction = BankTransaction.objects.filter(
        expense_group_id=expense_group.id
    ).first()
    bank_transaction.expense_group_id = 4
    bank_transaction.save()

    task_log = TaskLog.objects.filter(bank_transaction_id=bank_transaction.id).first()
    task_log.status = "READY"
    task_log.save()

    schedule_bank_transaction_creation(
        workspace_id=workspace_id, expense_group_ids=[5], is_auto_export=False, interval_hours=0, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False
    )


def test_create_bank_transactions_exceptions(db):
    workspace_id = 1

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.type = "CREATING_BANK_TRANSACTION"
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=5)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

        bank_transaction_lineitems = BankTransactionLineItem.objects.get(
            expense_id=expense.id
        )
        bank_transaction_lineitems.delete()

    expense_group.expenses.set(expenses)

    general_settings = WorkspaceGeneralSettings.objects.get(
        workspace_id=expense_group.workspace_id
    )
    general_settings.map_merchant_to_contact = False
    general_settings.auto_map_employees = True
    general_settings.auto_create_destination_entity = True
    general_settings.save()

    with mock.patch("apps.xero.utils.XeroConnector.post_bank_transaction") as mock_call:
        mock_call.side_effect = XeroCredentials.DoesNotExist()
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == "FAILED"

        mock_call.side_effect = BulkError(
            msg="employess not found", response="mapping error"
        )
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = InvalidGrant(
            msg="invalid grant", response="invalid grant"
        )
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = RateLimitError(
            msg="rate limit exceeded", response="rate limit exceeded"
        )
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = NoPrivilegeError(
            msg="no privilage error", response="no privilage error"
        )
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = XeroSDKError(
            msg="xerosdk error", response="xerosdk error"
        )
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = Exception()
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = WrongParamsError(
            msg={"Message": "Invalid parametrs"}, response="Invalid params"
        )
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        mock_call.side_effect = WrongParamsError(
            {
                "ErrorNumber": 10,
                "Type": "ValidationException",
                "Message": "A validation exception occurred",
                "Elements": [
                    {
                        "BankAccount": {
                            "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4",
                            "Code": "090",
                            "ValidationErrors": [],
                        },
                        "Type": "SPEND",
                        "Reference": "E/2022/03/T/1",
                        "Url": "None/app/admin/#/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn",
                        "IsReconciled": False,
                        "Contact": {
                            "ContactID": "73e6b7fb-ba7e-4b0a-a08b-f971b8ebbed8",
                            "Addresses": [],
                            "Phones": [],
                            "ContactGroups": [],
                            "ContactPersons": [],
                            "HasValidationErrors": False,
                            "ValidationErrors": [],
                        },
                        "DateString": "2022-03-30T00:00:00",
                        "Date": "/Date(1648598400000+0000)/",
                        "Status": "AUTHORISED",
                        "LineAmountTypes": "Exclusive",
                        "LineItems": [
                            {
                                "Description": "ashwin.t@fyle.in, category - Food spent on 2022-03-30, report number - C/2022/03/R/1  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn",
                                "UnitAmount": 92.38,
                                "TaxType": "OUTPUT",
                                "TaxAmount": 7.62,
                                "LineAmount": 92.38,
                                "AccountCode": "425",
                                "Tracking": [],
                                "Quantity": 1.0,
                                "AccountID": "c4b1c463-9913-4672-a8b8-01a3b546126f",
                                "ValidationErrors": [],
                            }
                        ],
                        "SubTotal": 92.38,
                        "TotalTax": 7.62,
                        "Total": 100.0,
                        "CurrencyCode": "USD",
                        "ValidationErrors": [
                            {"Message": "Url must be a valid absolute url"}
                        ],
                    }
                ],
            }
        )
        create_bank_transaction(expense_group.id, task_log.id, False, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == "FAILED"


def test_create_payment(mocker, db):
    mocker.patch("apps.xero.utils.XeroConnector.post_payment", return_value={})
    workspace_id = 1

    mocker.patch(
        "fyle.platform.apis.v1.admin.Reimbursements.list_all",
        return_value=fyle_data["get_all_reimbursements"],
    )

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expense'])

    bills = Bill.objects.all()
    expenses = []

    for bill in bills:
        expenses.extend(bill.expense_group.expenses.all())

    for expense in expenses:
        Reimbursement.objects.update_or_create(
            settlement_id=expense.settlement_id,
            reimbursement_id="qwertyuio",
            state="COMPLETE",
            workspace_id=workspace_id,
        )

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    general_mappings.payment_account_id = "2"
    general_mappings.save()

    create_payment(workspace_id)

    task_log = TaskLog.objects.filter(
        task_id="PAYMENT_{}".format(bill.expense_group.id)
    ).first()
    assert task_log.status == "COMPLETE"

    bill = Bill.objects.last()
    bill.payment_synced = False
    bill.save()

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_credentials.delete()

    try:
        create_payment(workspace_id)
    except Exception:
        logger.info("Xero Account not connected")


def test_create_payment_exceptions(mocker, db):
    workspace_id = 1

    mocker.patch(
        "fyle.platform.apis.v1.admin.Reimbursements.list_all",
        return_value=fyle_data["get_all_reimbursements"],
    )

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expense'])

    bills = Bill.objects.all()
    expenses = []

    for bill in bills:
        expenses.extend(bill.expense_group.expenses.all())

    for expense in expenses:
        Reimbursement.objects.update_or_create(
            settlement_id=expense.settlement_id,
            reimbursement_id="qwertyuio",
            state="COMPLETE",
            workspace_id=workspace_id,
        )

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    general_mappings.payment_account_id = "2"
    general_mappings.save()

    with mock.patch("apps.workspaces.models.XeroCredentials.objects.get") as mock_call:
        mock_call.side_effect = BulkError(
            msg="employess not found", response="mapping error"
        )
        create_payment(workspace_id)
        task_log = TaskLog.objects.filter(
            workspace_id=workspace_id, detail="mapping error"
        ).first()
        assert task_log.status == "FAILED"

        mock_call.side_effect = WrongParamsError(
            msg="wrong parameter", response="invalid parameter"
        )

        now = datetime.now().replace(tzinfo=timezone.utc)
        updated_at = now - timedelta(days=10)

        task_log = TaskLog.objects.filter(task_id='PAYMENT_{}'.format(bill.expense_group.id)).update(updated_at=updated_at)
        create_payment(workspace_id)
        task_log = TaskLog.objects.filter(
            workspace_id=workspace_id, detail="wrong parameter"
        ).first()
        assert task_log.status == "FAILED"

        mock_call.side_effect = Exception()
        create_payment(workspace_id)


def test_schedule_payment_creation(db):
    workspace_id = 1

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    general_mappings.payment_account_id = "2"
    general_mappings.save()

    schedule_payment_creation(
        sync_fyle_to_xero_payments=True, workspace_id=workspace_id
    )
    schedule = Schedule.objects.filter(func="apps.xero.tasks.create_payment").count()

    assert schedule == 1

    schedule_payment_creation(
        sync_fyle_to_xero_payments=False, workspace_id=workspace_id
    )
    schedule = Schedule.objects.filter(func="apps.xero.tasks.create_payment").count()

    assert schedule == 0


def test_check_xero_object_status(mocker, db):
    mocker.patch(
        "apps.xero.utils.XeroConnector.get_bill", return_value=data["bill_object"]
    )
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=4)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

    expense_group.expenses.set(expenses)
    expense_group.save()

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = "READY"
    task_log.expense_group = expense_group
    task_log.save()

    create_bill(expense_group.id, task_log.id, False, False)
    task_log = TaskLog.objects.get(id=task_log.id)

    check_xero_object_status(workspace_id)
    bills = Bill.objects.filter(expense_group_id=expense_group.id)

    for bill in bills:
        assert bill.paid_on_xero == True
        assert bill.payment_synced == True

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_credentials.delete()

    check_xero_object_status(workspace_id)


def test_schedule_reimbursements_sync(db):
    workspace_id = 1

    schedule = Schedule.objects.filter(
        func="apps.xero.tasks.process_reimbursements", args=workspace_id
    ).count()
    assert schedule == 1

    schedule_reimbursements_sync(
        sync_xero_to_fyle_payments=True, workspace_id=workspace_id
    )

    schedule_count = Schedule.objects.filter(
        func="apps.xero.tasks.process_reimbursements", args=workspace_id
    ).count()
    assert schedule_count == 1

    schedule_reimbursements_sync(
        sync_xero_to_fyle_payments=False, workspace_id=workspace_id
    )

    schedule_count = Schedule.objects.filter(
        func="apps.xero.tasks.process_reimbursements", args=workspace_id
    ).count()
    assert schedule_count == 0


def test_process_reimbursements(db, mocker):
    mocker.patch(
        "fyle_integrations_platform_connector.apis.Reports.bulk_mark_as_paid",
        return_value=[],
    )
    mocker.patch(
        "fyle_integrations_platform_connector.apis.Reimbursements.sync",
        return_value=[],
    )
    workspace_id = 1

    reimbursements = data["reimbursements"]

    expenses = Expense.objects.filter(fund_source="PERSONAL")
    for expense in expenses:
        expense.paid_on_xero = True
        expense.save()

    Reimbursement.create_or_update_reimbursement_objects(
        reimbursements=reimbursements, workspace_id=workspace_id
    )

    reimbursement_count = Reimbursement.objects.filter(
        workspace_id=workspace_id
    ).count()
    assert reimbursement_count == 4

    process_reimbursements(workspace_id)

    reimbursement = Reimbursement.objects.filter(workspace_id=workspace_id).count()

    assert reimbursement == 4


def test_schedule_xero_objects_status_sync(db):
    workspace_id = 1

    schedule_xero_objects_status_sync(
        sync_xero_to_fyle_payments=True, workspace_id=workspace_id
    )

    schedule_count = Schedule.objects.filter(
        func="apps.xero.tasks.check_xero_object_status", args=workspace_id
    ).count()
    assert schedule_count == 1

    schedule_xero_objects_status_sync(
        sync_xero_to_fyle_payments=False, workspace_id=workspace_id
    )

    schedule_count = Schedule.objects.filter(
        func="apps.xero.tasks.check_xero_object_status", args=workspace_id
    ).count()
    assert schedule_count == 0


def test_create_missing_currency(db, mocker):
    mocker.patch(
        "xerosdk.apis.Currencies.get_all",
        return_value={"Currencies": [{"Code": "INR"}]},
    )
    mocker.patch("xerosdk.apis.Currencies.post", return_value=[])
    workspace_id = 1

    create_missing_currency(workspace_id)

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.delete()

    create_missing_currency(workspace_id)


def test_update_xero_short_code(db, mocker):
    mocker.patch(
        "xerosdk.apis.Organisations.get_all",
        return_value=xero_data["get_all_organisations"],
    )
    workspace_id = 1

    update_xero_short_code(workspace_id)

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.delete()

    update_xero_short_code(workspace_id)


def test_update_last_export_details(db):
    workspace_id = 1

    last_export_detail = LastExportDetail.objects.create(workspace_id=workspace_id)
    last_export_detail.last_exported_at = datetime.now()
    last_export_detail.total_expense_groups_count = 1
    last_export_detail.save()

    last_export_detail = update_last_export_details(workspace_id=workspace_id)

    assert last_export_detail.total_expense_groups_count == 0


def test__validate_expense_group(mocker, db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.filter(fund_source="PERSONAL").first()

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.corporate_credit_card_expenses_object = "BANK TRANSACTION"
    general_settings.import_tax_codes = True
    general_settings.save()

    general_mapping = GeneralMapping.objects.get(workspace_id=workspace_id)
    general_mapping.default_tax_code_id = ""
    general_mapping.default_tax_code_name = ""
    general_mapping.save()

    employee_attribute = ExpenseAttribute.objects.filter(
        value=expense_group.description.get("employee_email"),
        workspace_id=expense_group.workspace_id,
        attribute_type="EMPLOYEE",
    ).first()

    mapping = Mapping.objects.get(
        destination_type="CONTACT",
        source_type="EMPLOYEE",
        source=employee_attribute,
        workspace_id=expense_group.workspace_id,
    )

    mapping.delete()

    try:
        __validate_expense_group(expense_group)
    except BulkError as exception:
        logger.info(exception.response)

    lineitem = expense_group.expenses.first()
    category = (
        lineitem.category
        if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None)
        else "{0} / {1}".format(lineitem.category, lineitem.sub_category)
    )

    category_attribute = ExpenseAttribute.objects.filter(
        value=category,
        workspace_id=expense_group.workspace_id,
        attribute_type="CATEGORY",
    ).first()

    account = Mapping.objects.filter(
        source_type="CATEGORY",
        source=category_attribute,
        workspace_id=expense_group.workspace_id,
    ).first()

    account.delete()

    try:
        __validate_expense_group(expense_group)
    except Exception:
        logger.info("Mappings are missing")

    general_mapping = GeneralMapping.objects.get(
        workspace_id=expense_group.workspace_id
    )
    general_mapping.delete()
    try:
        __validate_expense_group(expense_group)
    except Exception:
        logger.info("Mappings are missing")


def test_skipping_schedule_bills_creation(db, create_last_export_detail):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=4)
    expense_group.exported_at = None
    expense_group.save()

    bill = Bill.objects.get(expense_group_id=4)
    BillLineItem.objects.filter(bill=bill).delete()
    TaskLog.objects.filter(bill=bill).update(bill=None)
    bill.delete()

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.type = 'FETCHING_EXPENSES'
    task_log.status = "READY"
    task_log.save()

    error = Error.objects.create(
        workspace_id=workspace_id,
        type='NETSUITE_ERROR',
        error_title='NetSuite System Error',
        error_detail='An error occured in a upsert request: Please enter value(s) for: Location',
        expense_group_id=expense_group.id,
        repetition_count=106
    )

    schedule_bills_creation(
        workspace_id=workspace_id, expense_group_ids=[4], is_auto_export=True, interval_hours=1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False
    )

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'FETCHING_EXPENSES'

    Error.objects.filter(id=error.id).update(updated_at=datetime(2024, 8, 20))

    schedule_bills_creation(
        workspace_id=workspace_id, expense_group_ids=[4], is_auto_export=True, interval_hours=1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False
    )

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_BILL'


def test_skipping_schedule_bank_transaction_creation(db, create_last_export_detail):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=5)
    expense_group.exported_at = None
    expense_group.save()

    bank_tran = BankTransaction.objects.get(expense_group_id=5)
    BankTransactionLineItem.objects.filter(bank_transaction=bank_tran).delete()
    TaskLog.objects.filter(bank_transaction=bank_tran).update(bank_transaction=None)
    bank_tran.delete()

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    task_log.type = 'FETCHING_EXPENSES'
    task_log.status = "READY"
    task_log.save()

    error = Error.objects.create(
        workspace_id=workspace_id,
        type='NETSUITE_ERROR',
        error_title='NetSuite System Error',
        error_detail='An error occured in a upsert request: Please enter value(s) for: Location',
        expense_group_id=expense_group.id,
        repetition_count=106
    )

    schedule_bank_transaction_creation(
        workspace_id=workspace_id, expense_group_ids=[5], is_auto_export=True, interval_hours=1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False
    )

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'FETCHING_EXPENSES'

    Error.objects.filter(id=error.id).update(updated_at=datetime(2024, 8, 20))

    schedule_bank_transaction_creation(
        workspace_id=workspace_id, expense_group_ids=[5], is_auto_export=True, interval_hours=1, triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC, run_in_rabbitmq_worker=False
    )

    task_log = TaskLog.objects.filter(expense_group_id=expense_group.id).first()
    assert task_log.type == 'CREATING_BANK_TRANSACTION'


def test_skipping_payment(mocker, db):
    mocker.patch("apps.xero.utils.XeroConnector.post_payment", return_value={})
    workspace_id = 1

    mocker.patch(
        "fyle.platform.apis.v1.admin.Reimbursements.list_all",
        return_value=fyle_data["get_all_reimbursements"],
    )

    mocker.patch('fyle_integrations_platform_connector.apis.Expenses.get', return_value=data['expense'])

    bills = Bill.objects.all()
    expenses = []

    for bill in bills:
        expenses.extend(bill.expense_group.expenses.all())

    for expense in expenses:
        Reimbursement.objects.update_or_create(
            settlement_id=expense.settlement_id,
            reimbursement_id="qwertyuio",
            state="COMPLETE",
            workspace_id=workspace_id,
        )

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    general_mappings.payment_account_id = "2"
    general_mappings.save()

    task_log = TaskLog.objects.create(workspace_id=workspace_id, type='CREATING_PAYMENT', task_id='PAYMENT_{}'.format(bill.expense_group.id), status='FAILED')
    updated_at = task_log.updated_at
    create_payment(workspace_id)

    task_log = TaskLog.objects.get(workspace_id=workspace_id, type='CREATING_PAYMENT', task_id='PAYMENT_{}'.format(bill.expense_group.id))
    assert task_log.updated_at == updated_at

    now = datetime.now().replace(tzinfo=timezone.utc)
    updated_at = now - timedelta(days=25)
    # Update created_at to more than 2 months ago (more than 60 days)
    TaskLog.objects.filter(task_id='PAYMENT_{}'.format(bill.expense_group.id)).update(
        created_at=now - timedelta(days=61),  # More than 2 months ago
        updated_at=updated_at  # Updated within the last 1 month
    )

    task_log = TaskLog.objects.get(task_id='PAYMENT_{}'.format(bill.expense_group.id))

    create_payment(workspace_id)
    task_log.refresh_from_db()
    assert task_log.updated_at == updated_at

    updated_at = now - timedelta(days=25)
    # Update created_at to between 1 and 2 months ago (between 30 and 60 days)
    TaskLog.objects.filter(task_id='PAYMENT_{}'.format(bill.expense_group.id)).update(
        created_at=now - timedelta(days=45),  # Between 1 and 2 months ago
        updated_at=updated_at  # Updated within the last 1 month
    )
    create_payment(workspace_id)
    task_log.refresh_from_db()
    assert task_log.updated_at == updated_at


def test_get_or_create_error_with_expense_group_create_new(db):
    """
    Test creating a new error record
    """
    workspace_id = 1
    expense_group = ExpenseGroup.objects.get(id=1)

    expense_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        display_name='Employee',
        value='john.doe@fyle.in',
        source_id='test123'
    )

    error, created = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    assert created == True
    assert error.workspace_id == workspace_id
    assert error.type == 'EMPLOYEE_MAPPING'
    assert error.error_title == 'john.doe@fyle.in'
    assert error.error_detail == 'Employee mapping is missing'
    assert error.is_resolved == False
    assert error.mapping_error_expense_group_ids == [expense_group.id]


def test_get_or_create_error_with_expense_group_update_existing(db):
    """
    Test updating an existing error record with new expense group ID
    """
    workspace_id = 1
    expense_group = ExpenseGroup.objects.get(id=1)

    expense_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        display_name='Employee',
        value='john.doe@fyle.in',
        source_id='test123'
    )

    # Create initial error
    error1, created1 = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    # Get another expense group
    expense_group2 = ExpenseGroup.objects.get(id=2)

    # Try to create error with same attribute but different expense group
    error2, created2 = Error.get_or_create_error_with_expense_group(
        expense_group2,
        expense_attribute
    )

    assert created2 == False
    assert error2.id == error1.id
    assert set(error2.mapping_error_expense_group_ids) == {expense_group.id, expense_group2.id}


def test_get_or_create_error_with_expense_group_category_mapping(db):
    """
    Test creating category mapping error
    """
    workspace_id = 1
    expense_group = ExpenseGroup.objects.get(id=1)

    category_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        display_name='Category',
        value='Travel Test',
        source_id='test456'
    )

    error, created = Error.get_or_create_error_with_expense_group(
        expense_group,
        category_attribute
    )

    assert created == True
    assert error.type == 'CATEGORY_MAPPING'
    assert error.error_title == 'Travel Test'
    assert error.error_detail == 'Category mapping is missing'
    assert error.mapping_error_expense_group_ids == [expense_group.id]


def test_get_or_create_error_with_expense_group_duplicate_expense_group(db):
    """
    Test that adding same expense group ID twice doesn't create duplicate
    """
    workspace_id = 1
    expense_group = ExpenseGroup.objects.get(id=1)

    expense_attribute = ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        display_name='Employee',
        value='john.doe@fyle.in',
        source_id='test123'
    )

    # Create initial error
    error1, _ = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    # Try to add same expense group again
    error2, created2 = Error.get_or_create_error_with_expense_group(
        expense_group,
        expense_attribute
    )

    assert created2 == False
    assert error2.id == error1.id
    assert len(error2.mapping_error_expense_group_ids) == 1
    assert error2.mapping_error_expense_group_ids == [expense_group.id]


def test_handle_skipped_exports(mocker, db, create_last_export_detail):
    mock_post_summary = mocker.patch('apps.xero.queue.post_accounting_export_summary_for_skipped_exports', return_value=None)
    mock_update_last_export = mocker.patch('apps.xero.queue.update_last_export_details')
    mock_logger = mocker.patch('apps.xero.queue.logger')
    mocker.patch('apps.workspaces.helpers.patch_integration_settings', return_value=None)
    mocker.patch('apps.fyle.actions.post_accounting_export_summary', return_value=None)

    # Create or get two expense groups
    eg1 = ExpenseGroup.objects.create(workspace_id=1, fund_source='PERSONAL')
    eg2 = ExpenseGroup.objects.create(workspace_id=1, fund_source='PERSONAL')
    expense_groups = ExpenseGroup.objects.filter(id__in=[eg1.id, eg2.id])

    # Create a dummy error
    error = Error.objects.create(
        workspace_id=1,
        type='EMPLOYEE_MAPPING',
        expense_group=eg1,
        repetition_count=5,
        is_resolved=False,
        error_title='Test Error',
        error_detail='Test error detail',
    )

    # Case 1: triggered_by is DIRECT_EXPORT, not last export
    skip_export_count = 0
    result = handle_skipped_exports(
        expense_groups=expense_groups,
        index=0,
        skip_export_count=skip_export_count,
        error=error,
        expense_group=eg1,
        triggered_by=ExpenseImportSourceEnum.DIRECT_EXPORT
    )
    assert result == 1
    mock_post_summary.assert_called_once_with(eg1, eg1.workspace_id, is_mapping_error=False)
    mock_update_last_export.assert_not_called()
    mock_logger.info.assert_called()

    mock_post_summary.reset_mock()
    mock_update_last_export.reset_mock()
    mock_logger.reset_mock()

    # Case 2: last export, skip_export_count == total_count-1, should call update_last_export_details
    skip_export_count = 1
    result = handle_skipped_exports(
        expense_groups=expense_groups,
        index=1,
        skip_export_count=skip_export_count,
        error=None,
        expense_group=eg2,
        triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC
    )
    assert result == 2
    mock_post_summary.assert_not_called()
    mock_update_last_export.assert_called_once_with(eg2.workspace_id)
    mock_logger.info.assert_called()
