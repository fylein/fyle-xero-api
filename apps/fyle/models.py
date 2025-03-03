"""
Fyle Models
"""
import logging
from datetime import datetime
from typing import Dict, List

from dateutil import parser
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count, JSONField
from django.db.models.fields.json import KeyTextTransform
from fyle_accounting_mappings.mixins import AutoAddCreateUpdateInfoMixin
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_accounting_library.fyle_platform.constants import IMPORTED_FROM_CHOICES
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum

from apps.fyle.enums import ExpenseStateEnum, FundSourceEnum, PlatformExpensesEnum
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO


ALLOWED_FIELDS = [
    "employee_email",
    "report_id",
    "claim_number",
    "settlement_id",
    "fund_source",
    "vendor",
    "category",
    "project",
    "cost_center",
    "verified_at",
    "approved_at",
    "spent_at",
    "expense_id",
    "posted_at",
    "bank_transaction_id",
]


ALLOWED_FORM_INPUT = {
    "group_expenses_by": [
        "settlement_id",
        "claim_number",
        "report_id",
        "category",
        "vendor",
        "expense_id",
    ],
    "export_date_type": [
        "current_date",
        "approved_at",
        "spent_at",
        "verified_at",
        "last_spent_at",
        "posted_at",
    ],
}

SOURCE_ACCOUNT_MAP = {
    PlatformExpensesEnum.PERSONAL_CASH_ACCOUNT: FundSourceEnum.PERSONAL,
    PlatformExpensesEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT: FundSourceEnum.CCC,
}

SPLIT_EXPENSE_GROUPING = (('SINGLE_LINE_ITEM', 'SINGLE_LINE_ITEM'), ('MULTIPLE_LINE_ITEM', 'MULTIPLE_LINE_ITEM'))


def _format_date(date_string) -> datetime:
    """
    Format date.

    Args:
        date_string (str): Date string.

    Returns:
        dateime: Formatted date.
    """
    if date_string:
        date_string = parser.parse(date_string)

    return date_string


class Expense(models.Model):
    """
    Expense
    """

    id = models.AutoField(primary_key=True)
    employee_email = models.EmailField(
        max_length=255, unique=False, help_text="Email id of the Fyle employee"
    )
    employee_name = models.CharField(
        max_length=255, null=True, help_text="Name of the Fyle employee"
    )
    category = models.CharField(
        max_length=255, null=True, blank=True, help_text="Fyle Expense Category"
    )
    sub_category = models.CharField(
        max_length=255, null=True, blank=True, help_text="Fyle Expense Sub-Category"
    )
    project = models.CharField(
        max_length=255, null=True, blank=True, help_text="Project"
    )
    expense_id = models.CharField(max_length=255, unique=True, help_text="Expense ID")
    org_id = models.CharField(max_length=255, null=True, help_text="Organization ID")
    expense_number = models.CharField(max_length=255, help_text="Expense Number")
    claim_number = models.CharField(max_length=255, help_text="Claim Number", null=True)
    amount = models.FloatField(help_text="Home Amount")
    currency = models.CharField(max_length=5, help_text="Home Currency")
    foreign_amount = models.FloatField(null=True, help_text="Foreign Amount")
    foreign_currency = models.CharField(
        null=True, max_length=5, help_text="Foreign Currency"
    )
    settlement_id = models.CharField(
        max_length=255, help_text="Settlement ID", null=True
    )
    reimbursable = models.BooleanField(
        default=False, help_text="Expense reimbursable or not"
    )
    state = models.CharField(max_length=255, help_text="Expense state")
    vendor = models.CharField(max_length=255, null=True, blank=True, help_text="Vendor")
    cost_center = models.CharField(
        max_length=255, null=True, blank=True, help_text="Fyle Expense Cost Center"
    )
    corporate_card_id = models.CharField(
        max_length=255, null=True, blank=True, help_text="Corporate Card ID"
    )
    purpose = models.TextField(null=True, blank=True, help_text="Purpose")
    report_id = models.CharField(max_length=255, help_text="Report ID")
    bank_transaction_id = models.CharField(max_length=255, null=True, blank=True, help_text='Bank Transaction ID')
    billable = models.BooleanField(default=False, help_text="Expense billable or not")
    file_ids = ArrayField(
        base_field=models.CharField(max_length=255), null=True, help_text="File IDs"
    )
    spent_at = models.DateTimeField(null=True, help_text="Expense spent at")
    approved_at = models.DateTimeField(null=True, help_text="Expense approved at")
    posted_at = models.DateTimeField(
        null=True, help_text="Date when the money is taken from the bank"
    )
    is_posted_at_null = models.BooleanField(default=False, help_text='Flag check if posted at is null or not')
    expense_created_at = models.DateTimeField(help_text="Expense created at")
    expense_updated_at = models.DateTimeField(help_text="Expense created at")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")
    fund_source = models.CharField(max_length=255, help_text="Expense fund source")
    verified_at = models.DateTimeField(help_text="Report verified at", null=True)
    custom_properties = JSONField(null=True)
    paid_on_xero = models.BooleanField(
        help_text="Expense Payment status on Xero", default=False
    )
    paid_on_fyle = models.BooleanField(help_text="Expense Payment status on Fyle", default=False)
    tax_amount = models.FloatField(null=True, help_text="Tax Amount")
    tax_group_id = models.CharField(null=True, max_length=255, help_text="Tax Group ID")
    accounting_export_summary = JSONField(default=dict)
    previous_export_state = models.CharField(max_length=255, help_text='Previous export state', null=True)
    imported_from = models.CharField(choices=IMPORTED_FROM_CHOICES, max_length=255, help_text='Imported from source', null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='To which workspace this expense belongs to', null=True)

    class Meta:
        db_table = "expenses"

    @staticmethod
    def create_expense_objects(expenses: List[Dict], workspace_id: int, skip_update:bool = False, imported_from: ExpenseImportSourceEnum = None):
        """
        Bulk create expense objects
        """
        expense_objects = []
        eliminated_expenses = []

        for expense in expenses:
            cutoff_date = _format_date("2021-08-01T00:00:00.000Z")
            if expense["expense_created_at"]:
                expense_created_at = _format_date(expense["expense_created_at"])

            expense_data_to_append = None
            if not skip_update:
                expense_data_to_append = {
                    'claim_number': expense['claim_number'],
                    'approved_at': expense['approved_at'],
                    "expense_created_at": expense["expense_created_at"],
                    "expense_updated_at": expense["expense_updated_at"]
                }

            defaults = {
                "employee_email": expense["employee_email"],
                "employee_name": expense["employee_name"],
                "category": expense["category"],
                "sub_category": expense["sub_category"],
                "project": expense["project"],
                "expense_number": expense["expense_number"],
                "org_id": expense["org_id"],
                "amount": expense["amount"],
                "currency": expense["currency"],
                "foreign_amount": expense["foreign_amount"],
                "foreign_currency": expense["foreign_currency"],
                "reimbursable": expense["reimbursable"],
                "state": expense["state"],
                "vendor": expense["vendor"][:250]
                if expense["vendor"]
                else None,
                "cost_center": expense["cost_center"],
                "corporate_card_id": expense["corporate_card_id"],
                "purpose": expense["purpose"],
                "report_id": expense["report_id"],
                "bank_transaction_id": expense["bank_transaction_id"],
                "file_ids": expense["file_ids"],
                "spent_at": expense["spent_at"],
                "posted_at": expense["posted_at"],
                "is_posted_at_null": expense["is_posted_at_null"],
                "fund_source": SOURCE_ACCOUNT_MAP[
                    expense["source_account_type"]
                ],
                "verified_at": expense["verified_at"],
                "custom_properties": expense["custom_properties"],
                "tax_amount": expense["tax_amount"]
                if expense["tax_amount"]
                else 0,
                "tax_group_id": expense["tax_group_id"],
                "billable": expense["billable"]
                if expense["billable"]
                else False,
                'workspace_id': workspace_id
            }

            if expense_data_to_append:
                defaults.update(expense_data_to_append)

            if skip_update or expense_created_at > cutoff_date:
                expense_object, created = Expense.objects.update_or_create(
                    expense_id=expense["id"],
                    defaults=defaults
                )

                # Only set imported_from for newly created expenses
                if created and imported_from:
                    expense_object.imported_from = imported_from
                    expense_object.save(
                        update_fields=['imported_from']
                    )

                if not ExpenseGroup.objects.filter(
                    expenses__id=expense_object.id
                ).first():
                    expense_objects.append(expense_object)

            else:
                eliminated_expenses.append(expense["id"])

        if eliminated_expenses:
            logger.info(
                "Expenses with ids {} are not eligible for import".format(
                    eliminated_expenses
                )
            )

        return expense_objects


def get_default_expense_group_fields():
    return ["employee_email", "report_id", "claim_number", "fund_source"]


def get_default_ccc_expense_group_fields():
    return ["employee_email", "report_id", "claim_number", "fund_source", "expense_id"]


def get_default_expense_state():
    return ExpenseStateEnum.PAYMENT_PROCESSING


def get_default_ccc_expense_state():
    return ExpenseStateEnum.PAID


def get_default_split_expense_grouping():
    return 'MULTIPLE_LINE_ITEM'


CCC_EXPENSE_STATE = (
    (ExpenseStateEnum.APPROVED, ExpenseStateEnum.APPROVED),
    (ExpenseStateEnum.PAYMENT_PROCESSING, ExpenseStateEnum.PAYMENT_PROCESSING),
    (ExpenseStateEnum.PAID, ExpenseStateEnum.PAID)
)


class ExpenseGroupSettings(AutoAddCreateUpdateInfoMixin, models.Model):
    """
    ExpenseGroupCustomizationSettings
    """

    id = models.AutoField(primary_key=True)
    reimbursable_expense_group_fields = ArrayField(
        base_field=models.CharField(max_length=100),
        default=get_default_expense_group_fields,
        help_text="list of fields reimbursable expense grouped by",
    )

    corporate_credit_card_expense_group_fields = ArrayField(
        base_field=models.CharField(max_length=100),
        default=get_default_ccc_expense_group_fields,
        help_text="list of fields ccc expenses grouped by",
    )

    expense_state = models.CharField(
        max_length=100,
        default=get_default_expense_state,
        help_text="state at which expenses are fetched (PAYMENT_PROCESSING / PAID)",
        null=False,
    )

    reimbursable_expense_state = models.CharField(
        max_length=100,
        default=get_default_expense_state,
        help_text="state at which the reimbursable expenses are fetched (PAYMENT_PROCESSING / PAID)",
        null=True,
    )
    ccc_expense_state = models.CharField(
        max_length=100,
        default=get_default_ccc_expense_state,
        choices=CCC_EXPENSE_STATE,
        help_text="state at which the ccc expenses are fetched (PAYMENT_PROCESSING /PAID)",
        null=True,
    )
    reimbursable_export_date_type = models.CharField(
        max_length=100, default="current_date", help_text="Export Date"
    )
    ccc_export_date_type = models.CharField(
        max_length=100, default="spent_at", help_text="CCC Export Date"
    )
    import_card_credits = models.BooleanField(
        help_text="Import Card Credits", default=False
    )
    split_expense_grouping = models.CharField(max_length=100, default=get_default_split_expense_grouping, choices=SPLIT_EXPENSE_GROUPING, help_text='specify line items for split expenses grouping')
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.PROTECT,
        help_text="To which workspace this expense group setting belongs to",
        related_name="expense_group_settings",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")

    class Meta:
        db_table = "expense_group_settings"

    @staticmethod
    def update_expense_group_settings(expense_group_settings: Dict, workspace_id: int, user):
        settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
        current_reimbursable_settings = list(settings.reimbursable_expense_group_fields)
        current_ccc_settings = list(settings.corporate_credit_card_expense_group_fields)

        reimbursable_grouped_by = []
        corporate_credit_card_expenses_grouped_by = []

        immutable_reimbursable_list = tuple(current_reimbursable_settings)
        immutable_ccc_list = tuple(current_ccc_settings)

        for field in immutable_reimbursable_list:
            if field in ALLOWED_FORM_INPUT["group_expenses_by"]:
                current_reimbursable_settings.remove(field)

        for field in immutable_ccc_list:
            if field in ALLOWED_FORM_INPUT["group_expenses_by"]:
                current_ccc_settings.remove(field)

        if "report_id" not in current_reimbursable_settings:
            if "claim_number" in current_reimbursable_settings:
                current_reimbursable_settings.remove("claim_number")
        else:
            current_reimbursable_settings.append("claim_number")

        if "report_id" not in current_ccc_settings:
            if "claim_number" in current_ccc_settings:
                current_ccc_settings.remove("claim_number")
        else:
            current_ccc_settings.append("claim_number")

        reimbursable_grouped_by.extend(current_reimbursable_settings)
        corporate_credit_card_expenses_grouped_by.extend(current_ccc_settings)

        reimbursable_grouped_by.extend(
            expense_group_settings["reimbursable_expense_group_fields"]
        )
        corporate_credit_card_expenses_grouped_by.extend(
            expense_group_settings["corporate_credit_card_expense_group_fields"]
        )

        reimbursable_grouped_by = list(set(reimbursable_grouped_by))
        corporate_credit_card_expenses_grouped_by = list(
            set(corporate_credit_card_expenses_grouped_by)
        )

        for field in ALLOWED_FORM_INPUT["export_date_type"]:
            if field in reimbursable_grouped_by:
                reimbursable_grouped_by.remove(field)

        for field in ALLOWED_FORM_INPUT["export_date_type"]:
            if field in corporate_credit_card_expenses_grouped_by:
                corporate_credit_card_expenses_grouped_by.remove(field)

        if expense_group_settings["reimbursable_export_date_type"] != "current_date":
            reimbursable_grouped_by.append(
                expense_group_settings["reimbursable_export_date_type"]
            )

        if expense_group_settings["ccc_export_date_type"] != "current_date":
            corporate_credit_card_expenses_grouped_by.append(
                expense_group_settings["ccc_export_date_type"]
            )

        if (
            "claim_number" in reimbursable_grouped_by
            and corporate_credit_card_expenses_grouped_by
        ):
            reimbursable_grouped_by.append("report_id")
            corporate_credit_card_expenses_grouped_by.append("report_id")

        import_card_credits = settings.import_card_credits
        if "import_card_credits" in expense_group_settings.keys():
            import_card_credits = expense_group_settings["import_card_credits"]

        return ExpenseGroupSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults={
                "reimbursable_expense_group_fields": reimbursable_grouped_by,
                "corporate_credit_card_expense_group_fields": corporate_credit_card_expenses_grouped_by,
                "expense_state": expense_group_settings["expense_state"],
                "reimbursable_expense_state": expense_group_settings[
                    "reimbursable_expense_state"
                ]
                if "reimbursable_expense_state" in expense_group_settings
                else expense_group_settings["expense_state"],
                "ccc_expense_state": expense_group_settings["ccc_expense_state"]
                if "ccc_expense_state" in expense_group_settings
                else expense_group_settings["expense_state"],
                "reimbursable_export_date_type": expense_group_settings[
                    "reimbursable_export_date_type"
                ],
                "ccc_export_date_type": expense_group_settings["ccc_export_date_type"],
                "import_card_credits": import_card_credits,
                'split_expense_grouping': expense_group_settings['split_expense_grouping'],
            },
            user=user
        )


def _group_expenses(expenses, group_fields, workspace_id):
    expense_ids = list(map(lambda expense: expense.id, expenses))
    expenses = Expense.objects.filter(id__in=expense_ids).all()

    custom_fields = {}

    for field in group_fields:
        if field.lower() not in ALLOWED_FIELDS:
            group_fields.pop(group_fields.index(field))
            field = ExpenseAttribute.objects.filter(
                workspace_id=workspace_id, attribute_type=field.upper()
            ).first()
            if field:
                custom_fields[field.attribute_type.lower()] = KeyTextTransform(
                    field.display_name, "custom_properties"
                )

    expense_groups = list(
        expenses.values(*group_fields, **custom_fields).annotate(
            total=Count("*"), expense_ids=ArrayAgg("id")
        )
    )
    return expense_groups


class ExpenseGroup(models.Model):
    """
    Expense Group
    """

    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        help_text="To which workspace this expense group belongs to",
    )
    fund_source = models.CharField(max_length=255, help_text="Expense fund source")
    response_logs = JSONField(help_text="Reponse log of the export", null=True)
    expenses = models.ManyToManyField(
        Expense, help_text="Expenses under this Expense Group"
    )
    description = JSONField(max_length=255, help_text="Description", null=True)
    employee_name = models.CharField(
        max_length=100, help_text="Expense Group Employee Name", null=True
    )
    export_url = models.CharField(max_length=255, help_text='Xero URL for the exported expenses', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    exported_at = models.DateTimeField(help_text="Exported at", null=True)
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")

    class Meta:
        db_table = "expense_groups"

    @staticmethod
    def create_expense_groups_by_report_id_fund_source(
        expense_objects: List[Expense], workspace_id
    ):
        """
        Group expense by report_id and fund_source
        """
        expense_group_settings = ExpenseGroupSettings.objects.get(
            workspace_id=workspace_id
        )

        reimbursable_expense_group_fields = (
            expense_group_settings.reimbursable_expense_group_fields
        )
        reimbursable_expenses = list(
            filter(lambda expense: expense.fund_source == "PERSONAL", expense_objects)
        )

        expense_groups = _group_expenses(
            reimbursable_expenses, reimbursable_expense_group_fields, workspace_id
        )

        corporate_credit_card_expense_group_field = (
            expense_group_settings.corporate_credit_card_expense_group_fields
        )
        corporate_credit_card_expenses = list(
            filter(lambda expense: expense.fund_source == "CCC", expense_objects)
        )

        if corporate_credit_card_expenses:
            workspace_general_settings = WorkspaceGeneralSettings.objects.get(
                workspace_id=workspace_id
            )
            ccc_export_module = workspace_general_settings.corporate_credit_card_expenses_object

            if ccc_export_module == "BANK TRANSACTION" and expense_group_settings.split_expense_grouping == 'MULTIPLE_LINE_ITEM':
                ccc_expenses_without_bank_transaction_id = list(
                    filter(lambda expense: not expense.bank_transaction_id, corporate_credit_card_expenses)
                )

                ccc_expenses_with_bank_transaction_id = list(
                    filter(lambda expense: expense.bank_transaction_id, corporate_credit_card_expenses)
                )

                if ccc_expenses_without_bank_transaction_id:
                    groups_without_bank_transaction_id = _group_expenses(
                        ccc_expenses_without_bank_transaction_id,
                        corporate_credit_card_expense_group_field,
                        workspace_id,
                    )
                    expense_groups.extend(groups_without_bank_transaction_id)

                if ccc_expenses_with_bank_transaction_id:
                    split_expense_group_fields = [
                        field for field in corporate_credit_card_expense_group_field
                        if field not in ('expense_id', 'expense_number')
                    ]
                    split_expense_group_fields.append('bank_transaction_id')

                    groups_with_bank_transaction_id = _group_expenses(
                        ccc_expenses_with_bank_transaction_id,
                        split_expense_group_fields,
                        workspace_id,
                    )
                    expense_groups.extend(groups_with_bank_transaction_id)

            else:
                corporate_credit_card_expense_groups = _group_expenses(
                    corporate_credit_card_expenses,
                    corporate_credit_card_expense_group_field,
                    workspace_id,
                )

                expense_groups.extend(corporate_credit_card_expense_groups)

        expense_group_objects = []

        for expense_group in expense_groups:
            if expense_group_settings.reimbursable_export_date_type == "last_spent_at":
                expense_group["last_spent_at"] = (
                    Expense.objects.filter(id__in=expense_group["expense_ids"])
                    .order_by("-spent_at")
                    .first()
                    .spent_at
                )

            if expense_group_settings.ccc_export_date_type == "last_spent_at":
                expense_group["last_spent_at"] = (
                    Expense.objects.filter(id__in=expense_group["expense_ids"])
                    .order_by("-spent_at")
                    .first()
                    .spent_at
                )

            employee_name = (
                Expense.objects.filter(id__in=expense_group["expense_ids"])
                .first()
                .employee_name
            )

            expense_ids = expense_group["expense_ids"]
            expense_group.pop("total")
            expense_group.pop("expense_ids")

            for key in expense_group:
                if key in ALLOWED_FORM_INPUT["export_date_type"]:
                    if expense_group[key]:
                        expense_group[key] = expense_group[key].strftime("%Y-%m-%d")
                    else:
                        expense_group[key] = datetime.now().strftime("%Y-%m-%d")

            expense_group_object = ExpenseGroup.objects.create(
                workspace_id=workspace_id,
                fund_source=expense_group["fund_source"],
                description=expense_group,
                employee_name=employee_name,
            )

            expense_group_object.expenses.add(*expense_ids)

            expense_group_objects.append(expense_group_object)

        return expense_group_objects


class Reimbursement(models.Model):
    """
    Reimbursements
    """

    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        help_text="To which workspace this reimbursement belongs to",
    )
    settlement_id = models.CharField(max_length=255, help_text="Fyle Settlement ID")
    reimbursement_id = models.CharField(
        max_length=255, help_text="Fyle Reimbursement ID"
    )
    state = models.CharField(max_length=255, help_text="Fyle Reimbursement State")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")

    class Meta:
        db_table = "reimbursements"

    @staticmethod
    def create_or_update_reimbursement_objects(
        reimbursements: List[Dict], workspace_id
    ):
        """
        Create or Update reimbursement attributes
        """
        reimbursement_id_list = [
            reimbursement["id"] for reimbursement in reimbursements
        ]
        existing_reimbursements = Reimbursement.objects.filter(
            reimbursement_id__in=reimbursement_id_list, workspace_id=workspace_id
        ).all()

        existing_reimbursement_ids = []
        primary_key_map = {}

        for existing_reimbursement in existing_reimbursements:
            existing_reimbursement_ids.append(existing_reimbursement.reimbursement_id)
            primary_key_map[existing_reimbursement.reimbursement_id] = {
                "id": existing_reimbursement.id,
                "state": existing_reimbursement.state,
            }

        attributes_to_be_created = []
        attributes_to_be_updated = []

        for reimbursement in reimbursements:
            reimbursement["state"] = (
                PlatformExpensesEnum.REIMBURSEMENT_COMPLETE if reimbursement["is_paid"] else PlatformExpensesEnum.REIMBURSEMENT_PENDING
            )
            if reimbursement["id"] not in existing_reimbursement_ids:
                attributes_to_be_created.append(
                    Reimbursement(
                        settlement_id=reimbursement["settlement_id"],
                        reimbursement_id=reimbursement["id"],
                        state=reimbursement["state"],
                        workspace_id=workspace_id,
                    )
                )
            else:
                if (
                    reimbursement["state"]
                    != primary_key_map[reimbursement["id"]]["state"]
                ):
                    attributes_to_be_updated.append(
                        Reimbursement(
                            id=primary_key_map[reimbursement["id"]]["id"],
                            state=reimbursement["state"],
                        )
                    )

        if attributes_to_be_created:
            Reimbursement.objects.bulk_create(attributes_to_be_created, batch_size=50)

        if attributes_to_be_updated:
            Reimbursement.objects.bulk_update(
                attributes_to_be_updated, fields=["state"], batch_size=50
            )

    @staticmethod
    def get_last_synced_at(workspace_id: int):
        """
        Get last synced at datetime
        :param workspace_id: Workspace Id
        :return: last_synced_at datetime
        """
        return (
            Reimbursement.objects.filter(workspace_id=workspace_id)
            .order_by("-updated_at")
            .first()
        )
