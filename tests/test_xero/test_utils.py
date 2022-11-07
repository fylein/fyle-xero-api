import base64
from asyncio.log import logger
from unittest import mock
from fyle_accounting_mappings.models import DestinationAttribute
from apps.xero.utils import XeroConnector, XeroCredentials
from .fixtures import data
from tests.helper import dict_compare_keys
from xerosdk.exceptions import WrongParamsError
from apps.workspaces.models import WorkspaceGeneralSettings, XeroCredentials
from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem, Payment


def test_get_or_create_contact(mocker, db):
    mocker.patch(
        'xerosdk.apis.Contacts.post',
        return_value=data['create_contact']
    )

    mocker.patch(
        'xerosdk.apis.Contacts.search_contact_by_contact_name',
        return_value=[],
    )

    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    contact_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CONTACT').count()
    assert contact_count == 48

    xero_connection.get_or_create_contact(contact_name='sample', email='sample@fyle.in', create=True)

    new_contact_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CONTACT').count()
    assert new_contact_count == 49

    xero_connection.get_or_create_contact(contact_name='sample', email='sample@fyle.in', create=True)

    new_contact_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CONTACT').count()
    assert new_contact_count == 49


def test_sync_tenants(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.Tenants.get_all',
        return_value=data['get_all_tenants']
    )

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    xero_connection.sync_tenants()
    
    tenant_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TENANT').count()
    assert tenant_count == 2


def test_get_tax_inclusive_amount(db):
    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    tax_inclusive_amount = xero_connection.get_tax_inclusive_amount(100, 4)
    assert tax_inclusive_amount == 100.0


def test_sync_tax_codes(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.TaxRates.get_all',
        return_value=data['get_all_tax_codes']
    )

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    tax_code_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    assert tax_code_count == 8

    xero_connection.sync_tax_codes()

    new_tax_code_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    assert new_tax_code_count == 8


def test_sync_accounts(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.Accounts.get_all'
    )

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    account_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT').count()
    assert account_count == 56

    xero_connection.sync_accounts()

    new_account_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ACCOUNT').count()
    assert new_account_count == 56
    

def test_sync_contacts(mocker, db):
    mocker.patch(
        'xerosdk.apis.Contacts.list_all_generator',
        return_value=data['get_all_contacts']
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    contact_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CONTACT').count()
    assert contact_count == 48

    xero_connection.sync_contacts()

    new_contact_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CONTACT').count()
    assert new_contact_count == 66


def test_sync_customers(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.Contacts.list_all_generator',
        return_value=data['get_all_contacts']
    )

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    customers_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CUSTOMER').count()
    assert customers_count == 14

    xero_connection.sync_customers()

    new_customers_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CUSTOMER').count()
    assert new_customers_count == 14


def test_sync_tracking_categories(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.TrackingCategories.get_all',
        return_value=data['get_all_tracking_categories']
    )

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    tracking_categories_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='tracking_categories').count()
    assert tracking_categories_count == 0

    xero_connection.sync_tracking_categories()

    new_tracking_categories_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='tracking_categories').count()
    assert new_tracking_categories_count == 0


def test_sync_items(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.Items.get_all',
        return_value=data['get_all_items']
    )
    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    items_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ITEM').count()
    assert items_count == 16

    xero_connection.sync_items()

    new_items_count = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='ITEM').count()
    assert new_items_count == 16


def test_get_bill(mocker, db):
    mocker.patch(
        'xerosdk.apis.Invoices.get_by_id',
        return_value=data['bill_response']
    )
    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    bill = xero_connection.get_bill(146)

    assert dict_compare_keys(bill, data['bill_response']) == []


def test_sync_dimensions(mocker, db):
    mocker.patch(
        'xerosdk.apis.Contacts.list_all_generator',
        return_value=[]
    )
    workspace_id = 1

    contact_count = DestinationAttribute.objects.filter(attribute_type='CONTACT', workspace_id=1).count()
    project_count = DestinationAttribute.objects.filter(attribute_type='PROJECT', workspace_id=1).count()
    categoty_count = DestinationAttribute.objects.filter(attribute_type='EXPENSE_CATEGORY', workspace_id=1).count()

    assert contact_count == 48
    assert project_count == 0
    assert categoty_count == 0

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)
    xero_connection.sync_dimensions(workspace_id)

    contact_count = DestinationAttribute.objects.filter(attribute_type='CONTACT', workspace_id=1).count()
    project_count = DestinationAttribute.objects.filter(attribute_type='PROJECT', workspace_id=1).count()
    categoty_count = DestinationAttribute.objects.filter(attribute_type='EXPENSE_CATEGORY', workspace_id=1).count()

    assert contact_count == 48
    assert project_count == 0
    assert categoty_count == 0


def test_sync_dimensions_exception(db):
    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    with mock.patch('xerosdk.apis.Accounts.get_all') as mock_call:
        mock_call.side_effect = Exception()
        xero_connection.sync_dimensions(workspace_id)

    with mock.patch('xerosdk.apis.Contacts.list_all_generator') as mock_call:
        mock_call.side_effect = Exception()
        xero_connection.sync_dimensions(workspace_id)
    
    with mock.patch('xerosdk.apis.Items.get_all') as mock_call:
        mock_call.side_effect = Exception()
        xero_connection.sync_dimensions(workspace_id)

    with mock.patch('xerosdk.apis.TrackingCategories.get_all') as mock_call:
        mock_call.side_effect = Exception()
        xero_connection.sync_dimensions(workspace_id)

    with mock.patch('xerosdk.apis.TaxRates.get_all') as mock_call:
        mock_call.side_effect = Exception()
        xero_connection.sync_dimensions(workspace_id)


def test_post_bill_exception(db):
    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    bill = Bill.objects.filter(expense_group_id=4).first()
    bill_lineitems = BillLineItem.objects.filter(bill_id=bill.id)
    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    try:
        with mock.patch('xerosdk.apis.Invoices.post') as mock_call:
            mock_call.side_effect = WrongParamsError(msg={
                'Elements': [{
                    'ValidationErrors': [{
                        'Message': ['The document date cannot be before the end of year lock date']
                    }]
                }]
            }, response='wrong params')
            xero_connection.post_bill(bill, bill_lineitems, workspace_general_setting)
    except:
        logger.info("Account period error")


def test_post_bank_transaction_exception(db):
    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    bank_transaction = BankTransaction.objects.filter(expense_group_id=5).first()
    bank_transaction_lineitems = BankTransactionLineItem.objects.filter(bank_transaction_id=bank_transaction.id)
    workspace_general_setting = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    try:
        with mock.patch('xerosdk.apis.BankTransactions.post') as mock_call:
            mock_call.side_effect = WrongParamsError(msg={
                'Elements': [{
                    'ValidationErrors': [{
                        'Message': ['The document date cannot be before the end of year lock date']
                    }]
                }]
            }, response='wrong params')
            xero_connection.post_bank_transaction(bank_transaction, bank_transaction_lineitems, workspace_general_setting)
    except:
        logger.info("Account period error")


def test_post_attachments(mocker, db):
    mocker.patch(
        'xerosdk.apis.Attachments.post_attachment',
        return_value=[]
    )

    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    attachments = xero_connection.post_attachments(ref_id='ref_id', ref_type='ref_type', attachments=[{
        'id': 'sdfgh',
        'name': 'sample',
        'download_url': base64.b64encode('https://aaa.bbb.cc/x232sds'.encode("ascii"))
    }])
    assert len(attachments) == 1


def test_post_payment(mocker, db):
    mocker.patch(
        'xerosdk.apis.Payments.post',
        return_value=[]
    )

    workspace_id = 1

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    created_payment = xero_connection.post_payment(payment=Payment(
        invoice_id='werty',
        account_id=346,
        amount=45,
        expense_group_id=4,
        workspace_id=workspace_id
    ))

    assert created_payment == []