import base64
from datetime import timedelta, datetime

from django.conf import settings
from typing import List, Dict

import unidecode

from xerosdk import XeroSDK

from apps.mappings.models import TenantMapping
from apps.workspaces.models import XeroCredentials
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute

from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem, Payment


class XeroConnector:
    """
    Xero utility functions
    """

    def __init__(self, credentials_object: XeroCredentials, workspace_id: int):
        client_id = settings.XERO_CLIENT_ID
        client_secret = settings.XERO_CLIENT_SECRET
        base_url = settings.XERO_BASE_URL

        self.connection = XeroSDK(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=credentials_object.refresh_token
        )

        self.workspace_id = workspace_id

        credentials_object.refresh_token = self.connection.refresh_token
        credentials_object.save()

    def get_organisations(self):
        """
        Get xero organisations
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        return self.connection.organisations.get_all()

    def sync_tenants(self):
        """
        sync xero tenants
        """
        tenants = self.connection.tenants.get_all()

        tenant_attributes = []

        for tenant in tenants:
            tenant_attributes.append({
                'attribute_type': 'TENANT',
                'display_name': 'Tenant',
                'value': tenant['tenantName'],
                'destination_id': tenant['tenantId']
            })

        tenant_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            tenant_attributes, self.workspace_id)
        return tenant_attributes

    def sync_accounts(self):
        """
        Get accounts
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        accounts = self.connection.accounts.get_all()['Accounts']

        account_attributes = []

        for account in accounts:

            detail = {
                'account_name': account['Name'],
                'account_type': account['Type'],
            }

            if account['Type'] == 'BANK':
                account_attributes.append({
                    'attribute_type': 'BANK_ACCOUNT',
                    'display_name': 'Bank Account',
                    'value': unidecode.unidecode(u'{0}'.format(account['Name'])).replace('/', '-'),
                    'destination_id': account['AccountID'],
                    'active': True if account['Status'] == 'ACTIVE' else False,
                    'detail': detail
                })

            elif account['Type'] == 'EXPENSE':
                account_attributes.append({
                    'attribute_type': 'ACCOUNT',
                    'display_name': 'Account',
                    'value': unidecode.unidecode(u'{0}'.format(account['Name'])).replace('/', '-'),
                    'destination_id': account['Code'],
                    'active': True if account['Status'] == 'ACTIVE' else False,
                    'detail': detail
                })

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            account_attributes, self.workspace_id)
        return account_attributes

    def sync_contacts(self):
        """
        Get contacts
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        contacts = self.connection.contacts.get_all()['Contacts']

        contact_attributes = []

        for contact in contacts:
            detail = {
                'email': contact['EmailAddress'] if('EmailAddress' in contact) else None
            }
            contact_attributes.append({
                'attribute_type': 'CONTACT',
                'display_name': 'Contact',
                'value': contact['Name'],
                'destination_id': contact['ContactID'],
                'detail': detail
            })

        contact_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            contact_attributes, self.workspace_id)
        return contact_attributes

    def sync_tracking_categories(self):
        """
        Get Tracking Categories
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        tracking_categories = self.connection.tracking_categories.get_all()['TrackingCategories']

        tracking_category_attributes = []

        for tracking_category in tracking_categories:
            for option in tracking_category['Options']:
                tracking_category_attributes.append({
                    'attribute_type': tracking_category['Name'].upper().replace(' ', '_'),
                    'display_name': tracking_category['Name'],
                    'value': option['Name'],
                    'destination_id': option['TrackingOptionID']
                })

        tracking_category_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            tracking_category_attributes, self.workspace_id)

        return tracking_category_attributes

    def sync_items(self):
        """
        Get Items
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        items = self.connection.items.get_all()['Items']

        item_attributes = []

        for item in items:
            item_attributes.append({
                'attribute_type': 'ITEM',
                'display_name': 'Item',
                'value': item['Code'],
                'destination_id': item['ItemID']
            })

        item_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            item_attributes, self.workspace_id)
        return item_attributes


    def post_contact(self, contact: ExpenseAttribute, auto_map_employee_preference: str):
        """
        Post contact to Xero
        :param contact: contact attribute to be created
        :param auto_map_employee_preference: Preference while doing auto map of employees
        :return: Contact Desination Attribute
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        xero_display_name = contact.detail['full_name']

        contact = {
            'Name': xero_display_name,
            'FirstName': xero_display_name.split(' ')[0],
            'LastName': xero_display_name.split(' ')[-1]
            if len(xero_display_name.split(' ')) > 1 else '',
            'EmailAddress': contact.value
        }

        created_contact = self.connection.contacts.post(contact)['Contacts'][0]

        created_contact = DestinationAttribute.bulk_upsert_destination_attributes([{
            'attribute_type': 'CONTACT',
            'display_name': 'Contact',
            'value': created_contact['Name'],
            'destination_id': created_contact['ContactID'],
            'detail': {
                'email': created_contact['EmailAddress']
            }
        }], self.workspace_id)[0]

        return created_contact

    @staticmethod
    def __construct_bill_lineitems(bill_lineitems: List[BillLineItem]) -> List[Dict]:
        """
        Create bill line items
        :return: constructed line items
        """
        lines = []

        for line in bill_lineitems:
            line = {
                'Description': line.description,
                'Quantity': '1',
                'UnitAmount': line.amount,
                'AccountCode': line.account_id,
                'ItemCode': line.item_code if line.item_code else None,
                'Tracking': line.tracking_categories if line.tracking_categories else None
            }
            lines.append(line)

        return lines

    def __construct_bill(self, bill: Bill, bill_lineitems: List[BillLineItem]) -> Dict:
        """
        Create a bill
        :return: constructed bill
        """
        bill_payload = {
            'Type': 'ACCPAY',
            'Contact': {
                'ContactID': bill.contact_id
            },
            'LineAmountTypes': 'NoTax',
            'Reference': bill.reference,
            'Date': bill.date,
            'DueDate': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'CurrencyCode': bill.currency,
            'Status': 'AUTHORISED',
            'LineItems': self.__construct_bill_lineitems(bill_lineitems)
        }
        return bill_payload

    def post_bill(self, bill: Bill, bill_lineitems: List[BillLineItem]):
        """
        Post vendor bills to Xero
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        bills_payload = self.__construct_bill(bill, bill_lineitems)
        created_bill = self.connection.invoices.post(bills_payload)
        return created_bill

    @staticmethod
    def __construct_bank_transaction_lineitems(bank_transaction_lineitems: List[BankTransactionLineItem]) -> List[Dict]:
        """
        Create bank transaction line items
        :return: constructed line items
        """
        lines = []

        for line in bank_transaction_lineitems:
            line = {
                'Description': line.description,
                'Quantity': '1',
                'UnitAmount': line.amount,
                'AccountCode': line.account_id,
                'ItemCode': line.item_code if line.item_code else None,
                'Tracking': line.tracking_categories if line.tracking_categories else None
            }
            lines.append(line)

        return lines

    def __construct_bank_transaction(self, bank_transaction: BankTransaction,
                                     bank_transaction_lineitems: List[BankTransactionLineItem]) -> Dict:
        """
        Create a bank transaction
        :return: constructed bank transaction
        """
        bank_transaction_payload = {
            'Type': 'SPEND',
            'Contact': {
                'ContactID': bank_transaction.contact_id
            },
            'BankAccount': {
                'AccountID': bank_transaction.bank_account_code
            },
            'LineAmountTypes': 'NoTax',
            'Reference': bank_transaction.reference,
            'Date': bank_transaction.transaction_date,
            'CurrencyCode': bank_transaction.currency,
            'Status': 'AUTHORISED',
            'LineItems': self.__construct_bank_transaction_lineitems(
                bank_transaction_lineitems=bank_transaction_lineitems)
        }
        return bank_transaction_payload

    def post_bank_transaction(self, bank_transaction: BankTransaction,
                              bank_transaction_lineitems: List[BankTransactionLineItem]):
        """
        Post bank transactions to Xero
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        bank_transaction_payload = self.__construct_bank_transaction(bank_transaction, bank_transaction_lineitems)
        created_bank_transaction = self.connection.bank_transactions.post(bank_transaction_payload)
        return created_bank_transaction

    def post_attachments(self, ref_id: str, ref_type: str, attachments: List[Dict]) -> List:
        """
        Link attachments to objects Xero
        :param prep_id: prep id for export
        :param ref_id: object id
        :param ref_type: type of object
        :param attachments: attachment[dict()]
        """

        if len(attachments):
            responses = []
            for attachment in attachments:
                response = self.connection.attachments.post_attachment(
                    endpoint=ref_type,
                    filename='{0}_{1}'.format(attachment['expense_id'], attachment['filename']),
                    data=base64.b64decode(attachment['content']),
                    guid=ref_id
                )

                responses.append(response)
            return responses
        return []

    @staticmethod
    def __construct_bill_payment(payment: Payment) -> Dict:
        """
        Create a bill payment
        :param payment: bill_payment object extracted from database
        :return: constructed bill payment
        """
        payment_payload = {
            'Payments': [
                {
                    'Invoice': {
                        'InvoiceId': payment.invoice_id
                    },
                    'Account': {
                        'AccountId': payment.account_id
                    },
                    'Amount': payment.amount
                }
            ]
        }

        return payment_payload

    def post_payment(self, payment: Payment):
        """
        Post payment to Xero
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        payment_payload = self.__construct_bill_payment(payment)
        created_payment = self.connection.payments.post(payment_payload)
        return created_payment

    def get_bill(self, bill_id: str):
        """
        Get Bill by id from Xero
        :param bill_id:
        :return:
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        bill = self.connection.invoices.get_by_id(invoice_id=bill_id)
        return bill
