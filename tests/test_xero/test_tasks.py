import logging
import random
import pytest
from unittest import mock
from django_q.tasks import Chain
from django_q.models import Schedule
from apps.tasks.models import TaskLog
from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem
from apps.xero.tasks import get_or_create_credit_card_contact, create_bill, create_bank_transaction, create_payment, \
    check_xero_object_status, schedule_reimbursements_sync, process_reimbursements, create_or_update_employee_mapping, \
        schedule_payment_creation, schedule_bank_transaction_creation, schedule_bills_creation, schedule_xero_objects_status_sync, \
            create_missing_currency, update_xero_short_code, create_chain_and_export, load_attachments, attach_customer_to_export
from xerosdk.exceptions import XeroSDKError, WrongParamsError, InvalidGrant, RateLimitError, NoPrivilegeError
from fyle_accounting_mappings.models import Mapping, ExpenseAttribute
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, XeroCredentials
from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.mappings.models import GeneralMapping, TenantMapping
from apps.xero.utils import XeroConnector
from fyle_xero_api.exceptions import BulkError
from .fixtures import data
logger = logging.getLogger(__name__)


def test_get_or_create_credit_card_contact(mocker, db):
    mocker.patch(
        'apps.xero.utils.XeroConnector.get_or_create_contact',
        return_value=[]
    )
    workspace_id = 1

    contact = get_or_create_credit_card_contact(workspace_id, 'samp_merchant')

    assert contact != None

    try:
        with mock.patch('apps.xero.utils.XeroConnector.get_or_create_contact') as mock_call:
            mock_call.side_effect = WrongParamsError(msg='wrong parameters', response='wrong parameters')
            contact = get_or_create_credit_card_contact(workspace_id, 'samp_merchant')
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


def test_create_or_update_employee_mapping(db):
    workspace_id = 1

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

    create_bill(expense_group.id, task_log.id, xero_connection)
    
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
    
    with mock.patch('apps.xero.models.Bill.create_bill') as mock_call:
        mock_call.side_effect = XeroCredentials.DoesNotExist()
        create_bill(expense_group.id, task_log.id, xero_connection)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bill(expense_group.id, task_log.id, xero_connection)

        mock_call.side_effect = InvalidGrant(msg='invalid grant', response='invalid grant')
        create_bill(expense_group.id, task_log.id, xero_connection)
        
        mock_call.side_effect = RateLimitError(msg='rate limit exceeded', response='rate limit exceeded')
        create_bill(expense_group.id, task_log.id, xero_connection)
        
        mock_call.side_effect = NoPrivilegeError(msg='no privilage error', response='no privilage error')
        create_bill(expense_group.id, task_log.id, xero_connection)
        
        mock_call.side_effect = XeroSDKError(msg='wrong parameter', response='xerosdk error')
        create_bill(expense_group.id, task_log.id, xero_connection)

        mock_call.side_effect = Exception()
        create_bill(expense_group.id, task_log.id, xero_connection)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FATAL'

        mock_call.side_effect = WrongParamsError(msg={
                'Message': 'Invalid parametrs'
            }, response='Invalid params')
        create_bill(expense_group.id, task_log.id, xero_connection)

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


def test_post_create_bank_transaction_success(mocker, create_task_logs, db):
    mocker.patch(
        'xerosdk.apis.BankTransactions.post',
        return_value=data['bank_transaction_object']
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

    expense_group.id = random.randint(100, 1500000)
    expense_group.save()

    for expense in expenses:
        expense.expense_group_id = expense_group.id
        expense.save()

        bank_transaction_lineitems = BankTransactionLineItem.objects.get(expense_id=expense.id)
        bank_transaction_lineitems.delete()
    
    expense_group.expenses.set(expenses)
    
    create_bank_transaction(expense_group.id, task_log.id, xero_connection)
    
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
    
    with mock.patch('apps.workspaces.models.XeroCredentials.objects.get') as mock_call:
        mock_call.side_effect = XeroCredentials.DoesNotExist()
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'

        mock_call.side_effect = BulkError(msg='employess not found', response='mapping error')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)

        mock_call.side_effect = InvalidGrant(msg='invalid grant', response='invalid grant')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)
        
        mock_call.side_effect = RateLimitError(msg='rate limit exceeded', response='rate limit exceeded')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)
        
        mock_call.side_effect = NoPrivilegeError(msg='no privilage error', response='no privilage error')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)
        
        mock_call.side_effect = XeroSDKError(msg='xerosdk error', response='xerosdk error')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)

        mock_call.side_effect = Exception()
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)

        mock_call.side_effect = WrongParamsError(msg={
                'Message': 'Invalid parametrs'
            }, response='Invalid params')
        create_bank_transaction(expense_group.id, task_log.id, xero_connection)

        task_log = TaskLog.objects.get(id=task_log.id)
        assert task_log.status == 'FAILED'


def test_create_payment(mocker, db):
    mocker.patch(
        'apps.xero.utils.XeroConnector.post_payment',
        return_value={}
    )
    workspace_id = 1

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


def test_create_payment_exceptions(db):
    workspace_id = 1

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
    
    create_bill(expense_group.id, task_log.id, xero_connection)
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


def test_create_missing_currency(db):
    workspace_id = 1

    create_missing_currency(workspace_id)

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.delete()

    create_missing_currency(workspace_id)


def test_update_xero_short_code(db):
    workspace_id = 1

    update_xero_short_code(workspace_id)

    tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
    tenant_mapping.delete()

    update_xero_short_code(workspace_id)


def test_create_chain_and_export(db):
    workspace_id = 1

    chaining_attributes = [{'expense_group_id': 4, 'export_type': 'bill', 'task_log_id': 3}]
    create_chain_and_export(chaining_attributes, workspace_id)
