from datetime import datetime
from typing import List

from django.conf import settings
from django.db import models
from django.db.models import JSONField
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping, MappingSetting

from apps.fyle.enums import FyleAttributeEnum
from apps.fyle.models import Expense, ExpenseGroup
from apps.mappings.models import GeneralMapping
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings


def get_tracking_category(expense_group: ExpenseGroup, lineitem: Expense):
    mapping_settings = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id
    ).all()

    tracking_categories = []

    default_expense_attributes = [
        FyleAttributeEnum.CATEGORY,
        FyleAttributeEnum.EMPLOYEE,
        FyleAttributeEnum.CORPORATE_CARD,
        FyleAttributeEnum.TAX_GROUP
    ]
    default_destination_attributes = ["ITEM"]

    for setting in mapping_settings:
        if (
            setting.source_field not in default_expense_attributes
            and setting.destination_field not in default_destination_attributes
        ):
            if setting.source_field == FyleAttributeEnum.PROJECT:
                source_value = lineitem.project
            elif setting.source_field == FyleAttributeEnum.COST_CENTER:
                source_value = lineitem.cost_center
            else:
                attribute = ExpenseAttribute.objects.filter(
                    attribute_type=setting.source_field,
                    workspace_id=expense_group.workspace_id,
                ).first()
                source_value = lineitem.custom_properties.get(
                    attribute.display_name, None
                )

            mapping: Mapping = Mapping.objects.filter(
                source_type=setting.source_field,
                destination_type=setting.destination_field,
                source__value=source_value,
                workspace_id=expense_group.workspace_id,
            ).first()
            if mapping:
                tracking_categories.append(
                    {
                        "Name": mapping.destination.display_name,
                        "Option": mapping.destination.value,
                    }
                )

    return tracking_categories


def get_transaction_date(expense_group: ExpenseGroup) -> str:
    if (
        "spent_at" in expense_group.description
        and expense_group.description["spent_at"]
    ):
        return expense_group.description["spent_at"]
    elif (
        "approved_at" in expense_group.description
        and expense_group.description["approved_at"]
    ):
        return expense_group.description["approved_at"]
    elif (
        "verified_at" in expense_group.description
        and expense_group.description["verified_at"]
    ):
        return expense_group.description["verified_at"]
    elif (
        "posted_at" in expense_group.description
        and expense_group.description["posted_at"]
    ):
        return expense_group.description["posted_at"]
    elif (
        "last_spent_at" in expense_group.description
        and expense_group.description["last_spent_at"]
    ):
        return expense_group.description["last_spent_at"]

    return datetime.now().strftime("%Y-%m-%d")


def get_item_code_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    item_setting: MappingSetting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id, destination_field="ITEM"
    ).first()

    item_code = None

    if item_setting:
        if item_setting.source_field == FyleAttributeEnum.PROJECT:
            source_value = lineitem.project
        elif item_setting.source_field == FyleAttributeEnum.COST_CENTER:
            source_value = lineitem.cost_center
        else:
            attribute = ExpenseAttribute.objects.filter(
                attribute_type=item_setting.source_field
            ).first()
            source_value = lineitem.custom_properties.get(attribute.display_name, None)

        mapping: Mapping = Mapping.objects.filter(
            source_type=item_setting.source_field,
            destination_type="ITEM",
            source__value=source_value,
            workspace_id=expense_group.workspace_id,
        ).first()

        if mapping:
            item_code = mapping.destination.value
    return item_code


def get_customer_id_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    customer_setting: MappingSetting = MappingSetting.objects.filter(
        workspace_id=expense_group.workspace_id,
        destination_field="CUSTOMER",
        source_field=FyleAttributeEnum.PROJECT,
    ).first()

    customer_id = None

    if customer_setting and lineitem.billable and lineitem.project:
        mapping: Mapping = Mapping.objects.filter(
            source_type=FyleAttributeEnum.PROJECT,
            destination_type="CUSTOMER",
            source__value=lineitem.project,
            workspace_id=expense_group.workspace_id,
        ).first()

        if mapping:
            customer_id = mapping.destination.destination_id
    return customer_id


def get_expense_purpose(workspace_id, lineitem, category, workspace_general_settings) -> str:

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    org_id = Workspace.objects.get(id=workspace_id).fyle_org_id
    memo_structure = workspace_general_settings.memo_structure

    fyle_url = fyle_credentials.cluster_domain if settings.BRAND_ID == 'fyle' else settings.FYLE_APP_URL

    details = {
        'employee_email': lineitem.employee_email,
        'merchant': '{}'.format(lineitem.vendor) if lineitem.vendor else '',
        'category': '{0}'.format(category) if lineitem.category else '',
        'purpose': '{0}'.format(lineitem.purpose) if lineitem.purpose else '',
        'report_number': '{0}'.format(lineitem.claim_number),
        'spent_on': '{0}'.format(lineitem.spent_at.date()) if lineitem.spent_at else '',
        'expense_link': '{0}/app/admin/company_expenses?txnId={1}&org_id={2}'.format(fyle_url, lineitem.expense_id, org_id)
    }

    memo_parts = []
    for field in memo_structure:
        if field in details and details[field]:
            memo_parts.append(details[field])

    memo = ' - '.join(memo_parts)

    return memo


def get_tax_code_id_or_none(expense_group: ExpenseGroup, lineitem: Expense):
    tax_code = None
    mapping: Mapping = Mapping.objects.filter(
        source_type=FyleAttributeEnum.TAX_GROUP,
        destination_type="TAX_CODE",
        source__source_id=lineitem.tax_group_id,
        workspace_id=expense_group.workspace_id,
    ).first()
    if mapping:
        tax_code = mapping.destination.destination_id

    return tax_code


class Bill(models.Model):
    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(
        ExpenseGroup, on_delete=models.PROTECT, help_text="Expense group reference"
    )
    currency = models.CharField(max_length=255, help_text="Bill Currency")
    contact_id = models.CharField(max_length=255, help_text="Xero Contact")
    reference = models.CharField(max_length=255, help_text="Bill ID")
    date = models.DateTimeField(help_text="Bill date")
    payment_synced = models.BooleanField(
        help_text="Payment synced status", default=False
    )
    paid_on_xero = models.BooleanField(
        help_text="Payment status in Xero", default=False
    )
    is_retired = models.BooleanField(help_text='Is Payment sync retried', default=False)
    export_id = models.CharField(max_length=255, help_text="Export ID", null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")

    class Meta:
        db_table = "bills"

    @staticmethod
    def create_bill(expense_group: ExpenseGroup):
        description = expense_group.description

        expense: Expense = expense_group.expenses.first()

        contact: Mapping = Mapping.objects.get(
            destination_type="CONTACT",
            source_type=FyleAttributeEnum.EMPLOYEE,
            source__value=description.get("employee_email"),
            workspace_id=expense_group.workspace_id,
        )

        bill_object, _ = Bill.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                "currency": expense.currency,
                "contact_id": contact.destination.destination_id,
                "reference": expense.claim_number,
                "date": get_transaction_date(expense_group),
            },
        )

        return bill_object


class BillLineItem(models.Model):
    id = models.AutoField(primary_key=True)
    expense = models.OneToOneField(
        Expense, on_delete=models.PROTECT, help_text="Reference to Expense"
    )
    bill = models.ForeignKey(
        Bill, on_delete=models.PROTECT, help_text="Reference to Bill"
    )
    tracking_categories = JSONField(null=True, help_text="Save Tracking options")
    item_code = models.CharField(max_length=255, null=True, help_text="Item code")
    account_id = models.CharField(max_length=255, help_text="Xero account id")
    line_item_id = models.CharField(
        max_length=255, help_text="Xero line item id", null=True
    )
    customer_id = models.CharField(
        max_length=255, help_text="Xero customer id", null=True
    )
    description = models.TextField(help_text="Lineitem purpose")
    amount = models.FloatField(help_text="Bill amount")
    tax_amount = models.FloatField(null=True, help_text="Tax amount")
    tax_code = models.CharField(max_length=255, help_text="Tax Group ID", null=True)

    class Meta:
        db_table = "bill_lineitems"

    @staticmethod
    def create_bill_lineitems(expense_group: ExpenseGroup, workspace_general_settings: WorkspaceGeneralSettings):
        expenses = expense_group.expenses.all()
        bill = Bill.objects.get(expense_group=expense_group)

        bill_lineitem_objects = []

        for lineitem in expenses:
            category = (
                lineitem.category
                if (
                    lineitem.category == lineitem.sub_category
                    or lineitem.sub_category == None
                )
                else "{0} / {1}".format(lineitem.category, lineitem.sub_category)
            )

            account = Mapping.objects.filter(
                source_type=FyleAttributeEnum.CATEGORY,
                source__value=category,
                destination_type="ACCOUNT",
                workspace_id=expense_group.workspace_id,
            ).first()

            item_code = get_item_code_or_none(expense_group, lineitem)
            customer_id = get_customer_id_or_none(expense_group, lineitem)

            description = get_expense_purpose(
                expense_group.workspace_id, lineitem, category, workspace_general_settings
            )

            tracking_categories = get_tracking_category(expense_group, lineitem)

            lineitem_object, _ = BillLineItem.objects.update_or_create(
                bill=bill,
                expense_id=lineitem.id,
                defaults={
                    "tracking_categories": tracking_categories
                    if tracking_categories
                    else None,
                    "item_code": item_code if item_code else None,
                    "account_id": account.destination.destination_id,
                    "description": description,
                    "amount": lineitem.amount,
                    "tax_code": get_tax_code_id_or_none(expense_group, lineitem),
                    "tax_amount": lineitem.tax_amount,
                    "customer_id": customer_id,
                },
            )
            bill_lineitem_objects.append(lineitem_object)

        return bill_lineitem_objects


class BankTransaction(models.Model):
    """
    Xero Bank Transaction
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(
        ExpenseGroup, on_delete=models.PROTECT, help_text="Expense group reference"
    )
    contact_id = models.CharField(max_length=255, help_text="Xero Contact ID")
    bank_account_code = models.CharField(
        max_length=255, help_text="Xero Bank Account code"
    )
    currency = models.CharField(max_length=255, help_text="Bank Transaction Currency")
    reference = models.CharField(max_length=255, help_text="Bank Transaction ID")
    transaction_date = models.DateField(help_text="Bank transaction date")
    export_id = models.CharField(max_length=255, help_text="Export ID", null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")

    class Meta:
        db_table = "bank_transactions"

    @staticmethod
    def create_bank_transaction(
        expense_group: ExpenseGroup, map_merchant_to_contact: bool
    ):
        """
        Create bank transaction
        :param expense_group: expense group
        :return: bank transaction object
        """
        description = expense_group.description

        expense: Expense = expense_group.expenses.first()

        if map_merchant_to_contact:
            merchant = expense.vendor if expense.vendor else ""
            split_merchant = merchant.split()

            merchant = ' '.join(split_merchant)

            contact_id = DestinationAttribute.objects.filter(
                value__iexact=merchant,
                attribute_type="CONTACT",
                workspace_id=expense_group.workspace_id,
                active=True
            ).order_by("-updated_at").first()

            if not contact_id:
                contact_id = (
                    DestinationAttribute.objects.filter(
                        value__iexact="Credit Card Misc",
                        workspace_id=expense_group.workspace_id,
                    )
                    .first()
                    .destination_id
                )
            else:
                contact_id = contact_id.destination_id

        else:
            contact_id = Mapping.objects.get(
                source_type=FyleAttributeEnum.EMPLOYEE,
                destination_type="CONTACT",
                source__value=description.get("employee_email"),
                workspace_id=expense_group.workspace_id,
            ).destination.destination_id

        bank_account_id = None

        bank_account = Mapping.objects.filter(
            source_type=FyleAttributeEnum.CORPORATE_CARD,
            destination_type="BANK_ACCOUNT",
            source__source_id=expense.corporate_card_id,
            workspace_id=expense_group.workspace_id,
        ).first()
        if bank_account:
            bank_account_id = bank_account.destination.destination_id

        if not bank_account_id:
            bank_account_id = GeneralMapping.objects.get(
                workspace_id=expense_group.workspace_id
            ).bank_account_id

        bank_transaction_object, _ = BankTransaction.objects.update_or_create(
            expense_group=expense_group,
            defaults={
                "contact_id": contact_id,
                "bank_account_code": bank_account_id,
                "currency": expense.currency,
                "reference": expense.expense_number,
                "transaction_date": get_transaction_date(expense_group),
            },
        )
        return bank_transaction_object


class BankTransactionLineItem(models.Model):
    """
    Xero Bank Transaction Lineitem
    """

    id = models.AutoField(primary_key=True)
    expense = models.OneToOneField(
        Expense, on_delete=models.PROTECT, help_text="Reference to Expense"
    )
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.PROTECT,
        help_text="Reference to bank transaction",
    )
    account_id = models.CharField(max_length=255, help_text="Xero AccountCode")
    line_item_id = models.CharField(
        max_length=255, help_text="Xero line item id", null=True
    )
    customer_id = models.CharField(
        max_length=255, help_text="Xero customer id", null=True
    )
    item_code = models.CharField(max_length=255, help_text="Xero ItemCode", null=True)
    tracking_categories = JSONField(null=True, help_text="Save Tracking options")
    amount = models.FloatField(help_text="Bank Transaction LineAmount")
    description = models.TextField(
        help_text="Xero Bank Transaction LineItem description", null=True
    )
    tax_amount = models.FloatField(null=True, help_text="Tax amount")
    tax_code = models.CharField(max_length=255, help_text="Tax Group ID", null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")

    class Meta:
        db_table = "bank_transaction_lineitems"

    @staticmethod
    def create_bank_transaction_lineitems(expense_group: ExpenseGroup, workspace_general_settings: WorkspaceGeneralSettings):
        """
        Create bank transaction lineitems
        :param expense_group: expense group
        :return: lineitems objects
        """
        expenses = expense_group.expenses.all()
        bank_transaction = BankTransaction.objects.get(expense_group=expense_group)

        bank_transaction_lineitem_objects = []

        for lineitem in expenses:
            category = (
                lineitem.category
                if (
                    lineitem.category == lineitem.sub_category
                    or lineitem.sub_category == None
                )
                else "{0} / {1}".format(lineitem.category, lineitem.sub_category)
            )

            account: Mapping = Mapping.objects.filter(
                source_type=FyleAttributeEnum.CATEGORY,
                destination_type="ACCOUNT",
                source__value=category,
                workspace_id=expense_group.workspace_id,
            ).first()

            item_code = get_item_code_or_none(expense_group, lineitem)
            customer_id = get_customer_id_or_none(expense_group, lineitem)

            description = get_expense_purpose(
                expense_group.workspace_id, lineitem, category, workspace_general_settings
            )

            tracking_categories = get_tracking_category(expense_group, lineitem)

            (
                bank_transaction_lineitem_object,
                _,
            ) = BankTransactionLineItem.objects.update_or_create(
                bank_transaction=bank_transaction,
                expense_id=lineitem.id,
                defaults={
                    "account_id": account.destination.destination_id
                    if account
                    else None,
                    "item_code": item_code if item_code else None,
                    "tracking_categories": tracking_categories
                    if tracking_categories
                    else None,
                    "amount": lineitem.amount,
                    "description": description,
                    "tax_code": get_tax_code_id_or_none(expense_group, lineitem),
                    "tax_amount": lineitem.tax_amount,
                    "customer_id": customer_id,
                },
            )

            bank_transaction_lineitem_objects.append(bank_transaction_lineitem_object)

        return bank_transaction_lineitem_objects


class Payment(models.Model):
    """
    Xero Payments
    """

    id = models.AutoField(primary_key=True)
    expense_group = models.OneToOneField(
        ExpenseGroup, on_delete=models.PROTECT, help_text="Expense group reference"
    )
    amount = models.FloatField(help_text="Amount")
    workspace = models.ForeignKey(
        Workspace, on_delete=models.PROTECT, help_text="Workspace reference"
    )
    invoice_id = models.CharField(
        max_length=255, help_text="Linked Transaction ID ( Invoice ID )"
    )
    account_id = models.CharField(max_length=255, help_text="Payment Account")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")

    class Meta:
        db_table = "payments"

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
                "amount": total_amount,
                "invoice_id": invoice_id,
                "account_id": account_id,
            },
        )

        return payment_object
