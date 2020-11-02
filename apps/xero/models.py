from datetime import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
from fyle_accounting_mappings.models import Mapping, ExpenseAttribute, MappingSetting

from apps.fyle.models import ExpenseGroup, Expense

'''
  data = {
        "Type": "ACCREC",
        "Contact": {
            "ContactID": "fee2fb2a-97d5-4443-82df-796bc7758eb2"
        },
        "DueDateString": "2020-10-30T00:00:00",
        "LineAmountTypes": "NoTax",
        "Reference": "Reference TrackingCategoryID",
        "Url": "https://staging.fyle.tech/app/main/#/enterprise/view_expense/txOZD70Ue0AV",
        "Status": "AUTHORISED",
        "LineItems": [
            {
                "Description": "line item desc",
                "Quantity": "1",
                "UnitAmount": "321",
                "AccountCode": "260",
                "ItemCode": "BOOK",
                "Tracking": [
                    {
                        "TrackingCategoryID": "fa437cfd-f005-4538-ae84-943857da5c8c",
                        "Name": "Region",
                        "Option": "West Coast"
                    },
                    {
                        "TrackingCategoryID": "a955d51c-700b-4e26-8136-209a367ab12c",
                        "Option": "Ashwin"
                    },
                ]
            }
        ]
    }
'''


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


def get_expense_purpose(lineitem, category) -> str:
    expense_purpose = ', purpose - {0}'.format(lineitem.purpose) if lineitem.purpose else ''
    spent_at = ' spent on {0} '.format(lineitem.spent_at.date()) if lineitem.spent_at else ''
    return 'Expense by {0} against category {1}{2}with claim number - {3}{4}'.format(
        lineitem.employee_email, category, spent_at, lineitem.claim_number, expense_purpose)


class Bill(models.Model):
    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(ExpenseGroup, on_delete=models.PROTECT, help_text='Expense group reference')
    currency = models.CharField(max_length=255, help_text='Bill Currency')
    contact_id = models.CharField(max_length=255, help_text='Xero Contact')
    reference = models.CharField(max_length=255, help_text='Bill ID')
    date = models.DateTimeField(help_text='Bill date')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')

    @staticmethod
    def create_bill(expense_group: ExpenseGroup):
        description = expense_group.description

        expense: Expense = expense_group.expenses.first()

        contact: Mapping = Mapping.objects.get(
            destination_type='EMPLOYEE',
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


class BillLineItem:
    id = models.AutoField(primary_key=True)
    expense = models.OneToOneField(Expense, on_delete=models.PROTECT, help_text='Reference to Expense')
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to Bill')
    tracking_categories = JSONField(null=True, help_text='Save Tracking options')
    item_code = models.CharField(max_length=255, null=True, help_text='Item code')
    account_id = models.CharField(max_length=255, help_text='NetSuite account id')
    description = models.TextField(help_text='Lineitem purpose')
    amount = models.FloatField(help_text='Bill amount')

    @staticmethod
    def create_bill_line_item(expense_group: ExpenseGroup):
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
            description = get_expense_purpose(lineitem, category)

            tracking_categories = get_tracking_category(expense_group, lineitem)

            lineitem_object, _ = BillLineItem.objects.update_or_create(
                bill=bill,
                expense_id=lineitem.id,
                default={
                    'tracking_categories': tracking_categories,
                    'item_code': item_code,
                    'account_id': account.destination.destination_id,
                    'description': description,
                    'amount': lineitem.amount
                }
            )
            bill_lineitem_objects.append(lineitem_object)

        return bill_lineitem_objects
