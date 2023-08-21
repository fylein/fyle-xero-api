import logging
import random
from unittest import mock
from django_q.models import Schedule
from apps.tasks.models import TaskLog
from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem
from apps.xero.tasks import *
from apps.xero.tasks import __validate_expense_group
from xerosdk.exceptions import XeroSDKError, WrongParamsError, InvalidGrant, RateLimitError, NoPrivilegeError
from fyle_accounting_mappings.models import Mapping, ExpenseAttribute
from apps.workspaces.models import XeroCredentials, LastExportDetail
from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.mappings.models import GeneralMapping, TenantMapping
from apps.xero.utils import XeroConnector
from fyle_xero_api.exceptions import BulkError
from .fixtures import data
from tests.test_fyle.fixtures import data as fyle_data
from tests.test_xero.fixtures import data as xero_data

from apps.xero.exceptions import update_last_export_details

logger = logging.getLogger(__name__)


def test_get_or_create_credit_card_contact(mocker, db):
    mocker.patch(
        'apps.xero.utils.XeroConnector.get_or_create_contact',
        return_value=[]
    )
    workspace_id = 1

    contact = get_or_create_credit_card_contact(workspace_id, 'samp_merchant', False)
    assert contact == []

    contact = get_or_create_credit_card_contact(workspace_id, 'samp_merchant', True)
    assert contact == []

    try:
        with mock.patch('apps.xero.utils.XeroConnector.get_or_create_contact') as mock_call:
            mock_call.side_effect = [None, WrongParamsError(msg='wrong parameters', response='wrong parameters')]
            contact = get_or_create_credit_card_contact(workspace_id, 'samp_merchant', False)
    except:
        logger.info('wrong parameters')

    contact = get_or_create_credit_card_contact(workspace_id, '', True)
    assert contact == []

    mocker.patch(
        'apps.xero.utils.XeroConnector.get_or_create_contact',
        return_value={'name': 'Books by Bessie'}
    )

    contact = get_or_create_credit_card_contact(workspace_id, 'Books by Bessie', True)
    assert contact == {'name': 'Books by Bessie'}

    try:
        with mock.patch('apps.xero.utils.XeroConnector.get_or_create_contact') as mock_call:
            mock_call.side_effect = WrongParamsError(msg='wrong parameters', response='wrong parameters')
            contact = get_or_create_credit_card_contact(workspace_id, 'samp_merchant', False)
    except:
        logger.info('wrong parameters')


def test_load_attachments(mocker, db):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Files.bulk_generate_file_urls',
        return_value=[],
    )
    mocker.patch(
        'apps.xero.utils.XeroConnector.post_attachments',
        return_value=[],
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    expense_group = ExpenseGroup.objects.get(id=4)
    expenses = expense_group.expenses.all()

    for expense in expenses:
        expense.file_ids = ['asdfghj']
        expense.save()
    
    load_attachments(xero_connection, 'dfgh', 'werty', expense_group)

    with mock.patch('apps.xero.utils.XeroConnector.post_attachments') as mock_call:
        mock_call.side_effect = Exception()
        load_attachments(xero_connection, 'dfgh', 'werty', expense_group)


def test_attach_customer_to_export(mocker, db):
    mocker.patch(
        'xerosdk.apis.LinkedTransactions.post',
        return_value=[],
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    bill = Bill.objects.filter(id=4).first()
    bill_lineitems = BillLineItem.objects.get(bill_id=bill.id)
    bill_lineitems.customer_id = '234'
    bill_lineitems.save()

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BILL'
    task_log.bill = bill
    task_log.save()

    attach_customer_to_export(xero_connection, task_log)

    try:
        with mock.patch('xerosdk.apis.LinkedTransactions.post') as mock_call:
            mock_call.side_effect = Exception()
            attach_customer_to_export(xero_connection, task_log)
        assert 1 == 2
    except:
        logger.info('Something unexpected happened during attaching customer to export')


def test_create_or_update_employee_mapping(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.Contacts.search_contact_by_contact_name',
        return_value=data['create_contact']['Contacts'][0]
    )

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    expense_group = ExpenseGroup.objects.get(id=4)
    expense_group.description.update({'employee_email': 'ironman@fyle.in'})
    expense_group.save()

    source = ExpenseAttribute.objects.get(
            attribute_type='EMPLOYEE', value__iexact='ironman@fyle.in', workspace_id=workspace_id
        )
    mapping = Mapping.objects.filter(source=source)
    mapping.delete()

    create_or_update_employee_mapping(expense_group=expense_group, xero_connection=xero_connection, auto_map_employees_preference='EMAIL')

    with mock.patch('fyle_accounting_mappings.models.Mapping.create_or_update_mapping') as mock_call:
        mapping = Mapping.objects.filter(source=source)
        mapping.delete()
        
        mock_call.side_effect = WrongParamsError(msg='wrong parameters', response='wrong parameters')
        create_or_update_employee_mapping(expense_group=expense_group, xero_connection=xero_connection, auto_map_employees_preference='NAME')


def test_post_bill_success(mocker, create_task_logs, db):
    mocker.patch(
        'xerosdk.apis.Invoices.post',
        return_value=data['bill_object']
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BILL'
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

    create_bill(expense_group.id, task_log.id, xero_connection, False)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert bill.currency == 'USD'

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BILL'
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

    create_bill(expense_group.id, task_log.id, xero_connection, False)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    bill = Bill.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert bill.currency == 'USD'


def test_create_bill_exceptions(db):
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BILL'
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
    
    with mock.patch('apps.xero.utils.XeroConnector.post_bill') as mock_call:
        mock_call.side_effect = XeroCredentials.DoesNotExist()
        create_bill(expense_group.id, task_log.id, xero_connection, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bill(expense_group.id, task_log.id, xero_connection, False)

        mock_call.side_effect = InvalidGrant(msg='invalid grant', response='invalid grant')
        create_bill(expense_group.id, task_log.id, xero_connection, False)
        
        mock_call.side_effect = RateLimitError(msg='rate limit exceeded', response='rate limit exceeded')
        create_bill(expense_group.id, task_log.id, xero_connection, False)
        
        mock_call.side_effect = NoPrivilegeError(msg='no privilage error', response='no privilage error')
        create_bill(expense_group.id, task_log.id, xero_connection, False)
        
        mock_call.side_effect = XeroSDKError(msg='wrong parameter', response='xerosdk error')
        create_bill(expense_group.id, task_log.id, xero_connection, False)

        mock_call.side_effect = Exception()
        create_bill(expense_group.id, task_log.id, xero_connection, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        mock_call.side_effect = WrongParamsError(msg={
                'Message': 'Invalid parametrs'
            }, response='Invalid params')
        create_bill(expense_group.id, task_log.id, xero_connection, False)

        mock_call.side_effect = WrongParamsError({'ErrorNumber': 10, 'Type': 'ValidationException', 'Message': 'A validation exception occurred', 'Elements': [{'BankAccount': {'AccountID': '562555f2-8cde-4ce9-8203-0363922537a4', 'Code': '090', 'ValidationErrors': []}, 'Type': 'SPEND', 'Reference': 'E/2022/03/T/1', 'Url': 'None/app/admin/#/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn', 'IsReconciled': False, 'Contact': {'ContactID': '73e6b7fb-ba7e-4b0a-a08b-f971b8ebbed8', 'Addresses': [], 'Phones': [], 'ContactGroups': [], 'ContactPersons': [], 'HasValidationErrors': False, 'ValidationErrors': []}, 'DateString': '2022-03-30T00:00:00', 'Date': '/Date(1648598400000+0000)/', 'Status': 'AUTHORISED', 'LineAmountTypes': 'Exclusive', 'LineItems': [{'Description': 'ashwin.t@fyle.in, category - Food spent on 2022-03-30, report number - C/2022/03/R/1  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn', 'UnitAmount': 92.38, 'TaxType': 'OUTPUT', 'TaxAmount': 7.62, 'LineAmount': 92.38, 'AccountCode': '425', 'Tracking': [], 'Quantity': 1.0, 'AccountID': 'c4b1c463-9913-4672-a8b8-01a3b546126f', 'ValidationErrors': []}], 'SubTotal': 92.38, 'TotalTax': 7.62, 'Total': 100.0, 'CurrencyCode': 'USD', 'ValidationErrors': [{'Message': 'Url must be a valid absolute url'}]}]})
        create_bill(expense_group.id, task_log.id, xero_connection, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_schedule_bills_creation(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=4)
    expense_group.exported_at = None
    expense_group.save()

    bill = Bill.objects.filter(expense_group_id=expense_group.id).first()
    bill.expense_group_id = 5
    bill.save()

    task_log = TaskLog.objects.filter(bill_id=bill.id).first()
    task_log.status = 'READY'
    task_log.save()

    chaining_attributes = schedule_bills_creation(workspace_id=workspace_id, expense_group_ids=[4])
    assert len(chaining_attributes) == 1


def test_post_create_bank_transaction_success(mocker, db):
    mocker.patch(
        'xerosdk.apis.BankTransactions.post',
        return_value=data['bank_transaction_object']
    )

    mocker.patch(
        'xerosdk.apis.Contacts.search_contact_by_contact_name',
        return_value=data['create_contact']['Contacts'][0]
    )

    mocker.patch(
        'xerosdk.apis.Contacts.post',
        return_vaue=data['create_contact']['Contacts'][0]
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BANK_TRANSACTION'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=5)
    expenses = expense_group.expenses.all()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
        
        bank_transaction_lineitems = BankTransactionLineItem.objects.get(expense_id=expense.id)
        bank_transaction_lineitems.delete()
    
    expense_group.expenses.set(expenses)
    
    create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    bank_transaction = BankTransaction.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert bank_transaction.currency == 'USD'

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BANK_TRANSACTION'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=6)
    expenses = expense_group.expenses.all()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()
        
        bank_transaction_lineitems = BankTransactionLineItem.objects.get(expense_id=expense.id)
        bank_transaction_lineitems.delete()
    
    expense_group.expenses.set(expenses)
    
    create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)
    
    task_log = TaskLog.objects.get(pk=task_log.id)
    bank_transaction = BankTransaction.objects.get(expense_group_id=expense_group.id)

    assert task_log.status=='COMPLETE'
    assert bank_transaction.currency == 'USD'


def test_schedule_bank_transaction_creation(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=5)
    expense_group.exported_at = None
    expense_group.save()

    bank_transaction = BankTransaction.objects.filter(expense_group_id=expense_group.id).first()
    bank_transaction.expense_group_id = 4
    bank_transaction.save()

    task_log = TaskLog.objects.filter(bank_transaction_id=bank_transaction.id).first()
    task_log.status = 'READY'
    task_log.save()

    chaining_attributes = schedule_bank_transaction_creation(workspace_id=workspace_id, expense_group_ids=[5])
    assert len(chaining_attributes) == 1


def test_create_bank_transactions_exceptions(db):
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    task_log = TaskLog.objects.filter(workspace_id=workspace_id).first()
    task_log.status = 'READY'
    task_log.type = 'CREATING_BANK_TRANSACTION'
    task_log.save()

    expense_group = ExpenseGroup.objects.get(id=5)
    expenses = expense_group.expenses.all()

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

        bank_transaction_lineitems = BankTransactionLineItem.objects.get(expense_id=expense.id)
        bank_transaction_lineitems.delete()
    
    expense_group.expenses.set(expenses)

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
    general_settings.map_merchant_to_contact = False
    general_settings.auto_map_employees = True
    general_settings.auto_create_destination_entity = True
    general_settings.save()
    
    with mock.patch('apps.xero.utils.XeroConnector.post_bank_transaction') as mock_call:
        mock_call.side_effect = XeroCredentials.DoesNotExist()
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)

        mock_call.side_effect = InvalidGrant(msg='invalid grant', response='invalid grant')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)
        
        mock_call.side_effect = RateLimitError(msg='rate limit exceeded', response='rate limit exceeded')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)
        
        mock_call.side_effect = NoPrivilegeError(msg='no privilage error', response='no privilage error')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)
        
        mock_call.side_effect = XeroSDKError(msg='xerosdk error', response='xerosdk error')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)

        mock_call.side_effect = Exception()
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)

        mock_call.side_effect = WrongParamsError(msg={
                'Message': 'Invalid parametrs'
            }, response='Invalid params')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)

        mock_call.side_effect = WrongParamsError({'ErrorNumber': 10, 'Type': 'ValidationException', 'Message': 'A validation exception occurred', 'Elements': [{'BankAccount': {'AccountID': '562555f2-8cde-4ce9-8203-0363922537a4', 'Code': '090', 'ValidationErrors': []}, 'Type': 'SPEND', 'Reference': 'E/2022/03/T/1', 'Url': 'None/app/admin/#/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn', 'IsReconciled': False, 'Contact': {'ContactID': '73e6b7fb-ba7e-4b0a-a08b-f971b8ebbed8', 'Addresses': [], 'Phones': [], 'ContactGroups': [], 'ContactPersons': [], 'HasValidationErrors': False, 'ValidationErrors': []}, 'DateString': '2022-03-30T00:00:00', 'Date': '/Date(1648598400000+0000)/', 'Status': 'AUTHORISED', 'LineAmountTypes': 'Exclusive', 'LineItems': [{'Description': 'ashwin.t@fyle.in, category - Food spent on 2022-03-30, report number - C/2022/03/R/1  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txkImp4VID2Z?org_id=orhlmPm4H0wn', 'UnitAmount': 92.38, 'TaxType': 'OUTPUT', 'TaxAmount': 7.62, 'LineAmount': 92.38, 'AccountCode': '425', 'Tracking': [], 'Quantity': 1.0, 'AccountID': 'c4b1c463-9913-4672-a8b8-01a3b546126f', 'ValidationErrors': []}], 'SubTotal': 92.38, 'TotalTax': 7.62, 'Total': 100.0, 'CurrencyCode': 'USD', 'ValidationErrors': [{'Message': 'Url must be a valid absolute url'}]}]})
        create_bank_transaction(expense_group.id, task_log.id, xero_connection, False)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_create_payment(mocker, db):
    mocker.patch(
        'apps.xero.utils.XeroConnector.post_payment',
        return_value={}
    )
    workspace_id = 1

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Reimbursements.list_all',
        return_value=fyle_data['get_all_reimbursements']
    )

    bills = Bill.objects.all()
    expenses = []

    for bill in bills:
        expenses.extend(bill.expense_group.expenses.all())

    for expense in expenses:
        Reimbursement.objects.update_or_create(
            settlement_id=expense.settlement_id,
            reimbursement_id='qwertyuio',
            state='COMPLETE',
            workspace_id=workspace_id
        )

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    general_mappings.payment_account_id = '2'
    general_mappings.save()

    create_payment(workspace_id)

    task_log = TaskLog.objects.filter(task_id='PAYMENT_{}'.format(bill.expense_group.id)).first()
    assert task_log.status == 'COMPLETE'

    bill = Bill.objects.last()
    bill.payment_synced = False
    bill.save()

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_credentials.delete()

    try:
        create_payment(workspace_id)
    except:
        logger.info('Xero Account not connected')


def test_create_payment_exceptions(mocker, db):
    workspace_id = 1

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Reimbursements.list_all',
        return_value=fyle_data['get_all_reimbursements']
    )

    bills = Bill.objects.all()
    expenses = []

    for bill in bills:
        expenses.extend(bill.expense_group.expenses.all())

    for expense in expenses:
        Reimbursement.objects.update_or_create(
            settlement_id=expense.settlement_id,
            reimbursement_id='qwertyuio',
            state='COMPLETE',
            workspace_id=workspace_id
        )

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    general_mappings.payment_account_id = '2'
    general_mappings.save()
    
    with mock.patch('apps.workspaces.models.XeroCredentials.objects.get') as mock_call:
        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_payment(workspace_id)
        task_log = TaskLog.objects.filter(workspace_id=workspace_id, detail='mapping error').first()
        assert task_log.status == 'FAILED'

        mock_call.side_effect = WrongParamsError(msg='wrong parameter', response='invalid parameter')
        create_payment(workspace_id)
        task_log = TaskLog.objects.filter(workspace_id=workspace_id, detail='wrong parameter').first()
        assert task_log.status == 'FAILED'

        mock_call.side_effect = Exception()
        create_payment(workspace_id)


def test_schedule_payment_creation(db):
    workspace_id = 1

    general_mappings = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    general_mappings.payment_account_id = '2'
    general_mappings.save()

    schedule_payment_creation(sync_fyle_to_xero_payments=True, workspace_id=workspace_id)
    schedule = Schedule.objects.filter(func='apps.xero.tasks.create_payment').count()

    assert schedule == 1

    schedule_payment_creation(sync_fyle_to_xero_payments=False, workspace_id=workspace_id)
    schedule = Schedule.objects.filter(func='apps.xero.tasks.create_payment').count()

    assert schedule == 0


def test_check_xero_object_status(mocker, db):
    mocker.patch(
        'apps.xero.utils.XeroConnector.get_bill',
        return_value=data['bill_object']
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

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
    task_log.status = 'READY'
    task_log.expense_group = expense_group
    task_log.save()
    
    create_bill(expense_group.id, task_log.id, xero_connection, False)
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

    schedule = Schedule.objects.filter(func='apps.xero.tasks.process_reimbursements', args=workspace_id).count()
    assert schedule == 1

    schedule_reimbursements_sync(sync_xero_to_fyle_payments=True, workspace_id=workspace_id)

    schedule_count = Schedule.objects.filter(func='apps.xero.tasks.process_reimbursements', args=workspace_id).count()
    assert schedule_count == 1

    schedule_reimbursements_sync(sync_xero_to_fyle_payments=False, workspace_id=workspace_id)

    schedule_count = Schedule.objects.filter(func='apps.xero.tasks.process_reimbursements', args=workspace_id).count()
    assert schedule_count == 0


def test_process_reimbursements(db, mocker):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.bulk_post_reimbursements',
        return_value=[]
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Reimbursements.sync',
        return_value=[],
    )
    workspace_id = 1

    reimbursements = data['reimbursements']

    expenses = Expense.objects.filter(fund_source='PERSONAL')
    for expense in expenses:
        expense.paid_on_xero=True
        expense.save()

    Reimbursement.create_or_update_reimbursement_objects(reimbursements=reimbursements, workspace_id=workspace_id)

    reimbursement_count = Reimbursement.objects.filter(workspace_id=workspace_id).count()
    assert reimbursement_count == 4

    process_reimbursements(workspace_id)

    reimbursement = Reimbursement.objects.filter(workspace_id=workspace_id).count()

    assert reimbursement == 4


def test_schedule_xero_objects_status_sync(db):
    workspace_id = 1

    schedule_xero_objects_status_sync(sync_xero_to_fyle_payments=True, workspace_id=workspace_id)

    schedule_count = Schedule.objects.filter(func='apps.xero.tasks.check_xero_object_status', args=workspace_id).count()
    assert schedule_count == 1

    schedule_xero_objects_status_sync(sync_xero_to_fyle_payments=False, workspace_id=workspace_id)

    schedule_count = Schedule.objects.filter(func='apps.xero.tasks.check_xero_object_status', args=workspace_id).count()
    assert schedule_count == 0


def test_create_missing_currency(db, mocker):
    mocker.patch(
        'xerosdk.apis.Currencies.get_all',
        return_value={'Currencies': [{'Code': 'INR'}]}
    )
    mocker.patch(
        'xerosdk.apis.Currencies.post',
        return_value=[]
    )
    workspace_id = 1

    create_missing_currency(workspace_id)

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.delete()

    create_missing_currency(workspace_id)


def test_update_xero_short_code(db, mocker):
    mocker.patch(
        'xerosdk.apis.Organisations.get_all',
        return_value=xero_data['get_all_organisations']
    )
    workspace_id = 1

    update_xero_short_code(workspace_id)

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.delete()

    update_xero_short_code(workspace_id)


def test_create_chain_and_export(db):
    workspace_id = 1

    chaining_attributes = [{'expense_group_id': 4, 'export_type': 'bill', 'task_log_id': 3, 'last_export': False}]
    create_chain_and_export(chaining_attributes, workspace_id)


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

    expense_group = ExpenseGroup.objects.filter(fund_source='PERSONAL').first()

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.corporate_credit_card_expenses_object = 'BANK TRANSACTION'
    general_settings.import_tax_codes = True
    general_settings.save()

    general_mapping = GeneralMapping.objects.get(workspace_id=workspace_id)
    general_mapping.default_tax_code_id = ''
    general_mapping.default_tax_code_name = ''
    general_mapping.save()

    employee_attribute = ExpenseAttribute.objects.filter(
        value=expense_group.description.get('employee_email'),
        workspace_id=expense_group.workspace_id,
        attribute_type='EMPLOYEE'
    ).first()

    mapping = Mapping.objects.get(
        destination_type='CONTACT',
        source_type='EMPLOYEE',
        source=employee_attribute,
        workspace_id=expense_group.workspace_id
    )

    mapping.delete()

    try:
        __validate_expense_group(expense_group)
    except BulkError as exception:
        logger.info(exception.response)
    
    lineitem = expense_group.expenses.first()
    category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(
    lineitem.category, lineitem.sub_category)

    category_attribute = ExpenseAttribute.objects.filter(
        value=category,
        workspace_id=expense_group.workspace_id,
        attribute_type='CATEGORY'
    ).first()

    account = Mapping.objects.filter(
        source_type='CATEGORY',
        source=category_attribute,
        workspace_id=expense_group.workspace_id
    ).first()

    account.delete()

    try:
        __validate_expense_group(expense_group)
    except:
        logger.info('Mappings are missing')

    general_mapping = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)
    general_mapping.delete()
    try:
        __validate_expense_group(expense_group)
    except:
        logger.info('Mappings are missing')
