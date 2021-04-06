from datetime import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
from fyle_accounting_mappings.models import Mapping, ExpenseAttribute, MappingSetting
from typing import List

from apps.fyle.models import ExpenseGroup, Expense
from apps.mappings.models import GeneralMapping

from apps.fyle.utils import FyleConnector
from apps.workspaces.models import FyleCredential, Workspace


def get_tracking_category(expense_group: ExpenseGroup, lineitem: Expense):
    mapping_settings = MappingSetting.objects.filter(workspace_id=expense_group.workspace_id).all()

    tracking_categories = []
    default_expense_attributes = ['CATEGORY', 'EMPLOYEE']
    default_destination_attributes = ['ITEM']

    for setting in mapping_settings:
        if setting.source_field not in default_expense_attributes and \
                setting.destination_field not in default_destination_attributes:
            if setting.source_field == 'PROJECT':
                source_value = lineitem.project
            elif setting.source_field == 'COST_CENTER':
                source_value = lineitem.cost_center
            else:
                attribute = ExpenseAttribute.objects.filter(
                    attribute_type=setting.source_field,
                    workspace_id=expense_group.workspace_id
                ).first()
                source_value = lineitem.custom_properties.get(attribute.display_name, None)

            mapping: Mapping = Mapping.objects.filter(
                source_type=setting.source_field,
                destination_type=setting.destination_field,
                source__value=source_value,
                workspace_id=expense_group.workspace_id
            ).first()
            if mapping:
                tracking_categories.append({
                    'Name': mapping.destination.display_name,
                    'Option': mapping.destination.value
                })

    return tracking_categories


def get_transaction_date(expense_group: ExpenseGroup) -> str:
    if 'spent_at' in expense_group.description and expense_group.description['spent_at']:
        return expense_group.description['spent_at']
    elif 'approved_at' in expense_group.description and expense_group.description['approved_at']:
        return expense_group.description['approved_at']
    elif 'verified_at' in expense_group.description and expense_group.description['verified_at']:
        return expense_group.description['verified_at']
    elif 'last_spent_at' in expense_group.description and expense_group.description['last_spent_at']:
        return expense_group.description['last_spent_at']

    return datetime.now().strftime("%Y-%m-%d")


def get_item_code_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    item_setting: MappingSetting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id,
        destination_field='ITEM'
    ).first()

    item_code = None

    if item_setting:
        if item_setting.source_field == 'PROJECT':
            source_value = lineitem.project
        elif item_setting.source_field == 'COST_CENTER':
            source_value = lineitem.cost_center
        else:
            attribute = ExpenseAttribute.objects.filter(attribute_type=item_setting.source_field).first()
            source_value = lineitem.custom_properties.get(attribute.display_name, None)

        mapping: Mapping = Mapping.objects.filter(
            source_type=item_setting.source_field,
            destination_type='ITEM',
            source__value=source_value,
            workspace_id=expense_group.workspace_id
        ).first()

        if mapping:
            item_code = mapping.destination.value
    return item_code


def get_expense_purpose(workspace_id, lineitem, category) -> str:
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_connector = FyleConnector(
        refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)

    cluster_domain = fyle_connector.get_cluster_domain()

    org_id = Workspace.objects.get(id=workspace_id).fyle_org_id

    expense_link = '{0}/app/main/#/enterprise/view_expense/{1}?org_id={2}'.format(
        cluster_domain['cluster_domain'], lineitem.expense_id, org_id
    )

    expense_purpose = ', purpose - {0}'.format(lineitem.purpose) if lineitem.purpose else ''
    spent_at = ' spent on {0} '.format(lineitem.spent_at.date()) if lineitem.spent_at else ''
    return 'Expense by {0} against category {1}{2}with claim number - {3}{4} - {5}'.format(
        lineitem.employee_email, category, spent_at, lineitem.claim_number, expense_purpose, expense_link)


class Bill(models.Model):
    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    currency = models.CharField(max_length=255, help_text='Bill Currency')
    contact_id = models.CharField(max_length=255, help_text='Xero Contact')
    reference = models.CharField(max_length=255, help_text='Bill ID')
    date = models.DateTimeField(help_text='Bill date')
    payment_synced = models.BooleanField(help_text='Payment synced status', default=False)
    paid_on_xero = models.BooleanField(help_text='Payment status in Xero', default=False)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'bills'

    @staticmethod
    def create_bill(expense_group: ExpenseGroup):
        description = expense_group.description

        expense: Expense = expense_group.expenses.first()

        contact: Mapping = Mapping.objects.get(
            destination_type='CONTACT',
            source_type='EMPLOYEE',
            source__value=description.get('employee_email'),
            workspace_id=expense_group.workspace_id
        )

        bill_object, _ = Bill.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'currency': expense.currency,
                'contact_id': contact.destination.destination_id,
                'reference': '{} - {}'.format(expense_group.id, expense.employee_email),
                'date': get_transaction_date(expense_group)
            }
        )

        return bill_object


class BillLineItem(models.Model):
    id = models.AutoField(primary_key=True)
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to Bill')
    tracking_categories = JSONField(null=True, help_text='Save Tracking options')
    item_code = models.CharField(max_length=255, null=True, help_text='Item code')
    account_id = models.CharField(max_length=255, help_text='Xero account id')
    description = models.TextField(help_text='Lineitem purpose')
    amount = models.FloatField(help_text='Bill amount')

    class Meta:
        db_table = 'bill_lineitems'

    @staticmethod
    def create_bill_lineitems(expense_group: ExpenseGroup):
        expenses = expense_group.expenses.all()
        bill = Bill.objects.get(expense_group=expense_group)

        bill_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
                lineitem.category, lineitem.sub_category)

            account = Mapping.objects.filter(
                source_type='CATEGORY',
                source__value=category,
                destination_type='ACCOUNT',
                workspace_id=expense_group.workspace_id
            ).first()

            item_code = get_item_code_or_none(expense_group, lineitem)

            description = get_expense_purpose(expense_group.workspace_id, lineitem, category)

            tracking_categories = get_tracking_category(expense_group, lineitem)

            lineitem_object, _ = BillLineItem.objects.update_or_create(
                bill=bill,
                expense_id=lineitem.id,
                defaults={
                    'tracking_categories': tracking_categories if tracking_categories else None,
                    'item_code': item_code if item_code else None,
                    'account_id': account.destination.destination_id,
                    'description': description,
                    'amount': lineitem.amount
                }
            )
            bill_lineitem_objects.append(lineitem_object)

        return bill_lineitem_objects


class BankTransaction(models.Model):
    """
    Xero Bank Transaction
    """
    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    contact_id = models.CharField(max_length=255, help_text='Xero Contact ID')
    bank_account_code = models.CharField(max_length=255, help_text='Xero Bank Account code')
    currency = models.CharField(max_length=255, help_text='Bank Transaction Currency')
    reference = models.CharField(max_length=255, help_text='Bank Transaction ID')
    transaction_date = models.DateField(help_text='Bank transaction date')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'bank_transactions'

    @staticmethod
    def create_bank_transaction(expense_group: ExpenseGroup, map_merchant_to_contact: bool):
        """
        Create bank transaction
        :param expense_group: expense group
        :return: bank transaction object
        """
        description = expense_group.description

        expense: Expense = expense_group.expenses.first()

        if map_merchant_to_contact:
            merchant = expense.vendor if expense.vendor else ''

            contact_id = DestinationAttribute.objects.filter(
                value__iexact=merchant, attribute_type='CONTACT', workspace_id=expense_group.workspace_id
            ).first()

            if not contact_id:
                contact_id = DestinationAttribute.objects.filter(
                    value='Credit Card Misc', workspace_id=expense_group.workspace_id).first().destination_id
            else:
                contact_id = contact_id.destination_id

        else:
            contact_id = Mapping.objects.get(
                source_type='EMPLOYEE',
                destination_type='CONTACT',
                source__value=description.get('employee_email'),
                workspace_id=expense_group.workspace_id
            ).destination.destination_id

        general_mappings = GeneralMapping.objects.get(workspace_id=expense_group.workspace_id)

        bank_transaction_object, _ = BankTransaction.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                'contact_id': contact_id,
                'bank_account_code': general_mappings.bank_account_id,
                'currency': expense.currency,
                'reference': '{} - {}'.format(expense_group.id, expense.employee_email),
                'transaction_date': get_transaction_date(expense_group),
            }
        )
        return bank_transaction_object


class BankTransactionLineItem(models.Model):
    """
    Xero Bank Transaction Lineitem
    """
    id = models.AutoField(primary_key=True)
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    bank_transaction = models.ForeignKey(BankTransaction, on_delete=models.PROTECT,
                                         help_text='Reference to bank transaction')
    account_id = models.CharField(max_length=255, help_text='Xero AccountCode')
    item_code = models.CharField(max_length=255, help_text='Xero ItemCode', null=True)
    tracking_categories = JSONField(null=True, help_text='Save Tracking options')
    amount = models.FloatField(help_text='Bank Transaction LineAmount')
    description = models.TextField(help_text='Xero Bank Transaction LineItem description', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'bank_transaction_lineitems'

    @staticmethod
    def create_bank_transaction_lineitems(expense_group: ExpenseGroup):
        """
        Create bank transaction lineitems
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        bank_transaction = BankTransaction.objects.get(expense_group=expense_group)

        bank_transaction_lineitem_objects = []

        for lineitem in expenses:
            category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
                lineitem.category, lineitem.sub_category)

            account: Mapping = Mapping.objects.filter(
                source_type='CATEGORY',
                destination_type='ACCOUNT',
                source__value=category,
                workspace_id=expense_group.workspace_id
            ).first()

            item_code = get_item_code_or_none(expense_group, lineitem)

            description = get_expense_purpose(expense_group.workspace_id, lineitem, category)

            tracking_categories = get_tracking_category(expense_group, lineitem)

            bank_transaction_lineitem_object, _ = BankTransactionLineItem.objects.update_or_create(
                bank_transaction=bank_transaction,
                expense_id=lineitem.id,
                defaults={
                    'account_id': account.destination.destination_id if account else None,
                    'item_code': item_code if item_code else None,
                    'tracking_categories': tracking_categories if tracking_categories else None,
                    'amount': lineitem.amount,
                    'description': description
                }
            )

            bank_transaction_lineitem_objects.append(bank_transaction_lineitem_object)

        return bank_transaction_lineitem_objects


class Payment(models.Model):
    """
    Xero Payments
    """
    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    amount = models.FloatField(help_text='Amount')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Workspace reference')
    invoice_id = models.CharField(max_length=255, help_text='Linked Transaction ID ( Invoice ID )')
    account_id = models.CharField(max_length=255, help_text='Payment Account')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    class Meta:
        db_table = 'payments'

    @staticmethod
    def create_payment(expense_group: ExpenseGroup, invoice_id: str, account_id: str):
        expenses: List[Expense] = expense_group.expenses.all()

        total_amount = 0
        for expense in expenses:
            total_amount = total_amount + expense.amount

        payment_object, _ = Payment.objects.update_or_create(
            expense_group=expense_group,
            workspace=expense_group.workspace,
            defaults={
                'amount': total_amount,
                'invoice_id': invoice_id,
                'account_id': account_id
            }
        )

        return payment_object
