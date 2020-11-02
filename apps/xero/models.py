from datetime import datetime

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


def get_transaction_date(expense_group: ExpenseGroup) -> str:
    if 'spent_at' in expense_group.description and expense_group.description['spent_at']:
        return expense_group.description['spent_at']
    elif 'approved_at' in expense_group.description and expense_group.description['approved_at']:
        return expense_group.description['approved_at']
    elif 'verified_at' in expense_group.description and expense_group.description['verified_at']:
        return expense_group.description['verified_at']

    return datetime.now().strftime("%Y-%m-%d")


def get_item_id_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    item_setting: MappingSetting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id,
        destination_field='ITEM'
    ).first()

    item_id = None

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
            item_id = mapping.destination.destination_id
    return item_id


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
