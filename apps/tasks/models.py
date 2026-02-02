from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField
from fyle_accounting_library.fyle_platform.constants import IMPORTED_FROM_CHOICES
from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.models import ExpenseGroup
from apps.tasks.enums import ErrorTypeEnum
from apps.workspaces.models import Workspace
from apps.xero.models import BankTransaction, Bill, Payment


def get_default():
    return dict


def get_error_type_mapping(attribute_type: str) -> str:
    """
    Returns the error type string based on the attribute type.
    Defaults to 'CATEGORY_MAPPING' if the type is not explicitly mapped.
    """
    mapping = {
        'EMPLOYEE': ErrorTypeEnum.EMPLOYEE_MAPPING,
        'CATEGORY': ErrorTypeEnum.CATEGORY_MAPPING
    }
    return mapping.get(attribute_type, ErrorTypeEnum.CATEGORY_MAPPING)


class TaskLog(models.Model):
    """
    Table to store task logs
    """

    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.PROTECT, help_text="Reference to Workspace model"
    )
    type = models.CharField(
        max_length=50, help_text="Task type (FETCH_EXPENSES / CREATE_BILL)"
    )
    task_id = models.CharField(
        max_length=255, null=True, help_text="Django Q task reference"
    )
    expense_group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.PROTECT,
        null=True,
        help_text="Reference to Expense group",
        unique=True
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.PROTECT, help_text="Reference to Payment", null=True
    )
    bill = models.ForeignKey(
        Bill, on_delete=models.PROTECT, help_text="Reference to Bill", null=True
    )
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.PROTECT,
        help_text="Reference to Bank Transaction",
        null=True,
    )
    status = models.CharField(max_length=255, help_text="Task Status")
    detail = JSONField(help_text="Task response", null=True, default=get_default())
    xero_errors = JSONField(help_text="Xero Errors", null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")
    triggered_by = models.CharField(max_length=255, help_text="Triggered by", null=True, choices=IMPORTED_FROM_CHOICES)
    re_attempt_export = models.BooleanField(default=False, help_text='Is re-attempt export')
    stuck_export_re_attempt_count = models.IntegerField(default=0, help_text='Stuck export re-attempt count')
    is_attachment_upload_failed = models.BooleanField(default=False, help_text='Is attachment upload failed')

    class Meta:
        db_table = "task_logs"


ERROR_TYPE_CHOICES = (
    (ErrorTypeEnum.EMPLOYEE_MAPPING, ErrorTypeEnum.EMPLOYEE_MAPPING),
    (ErrorTypeEnum.CATEGORY_MAPPING, ErrorTypeEnum.CATEGORY_MAPPING),
    (ErrorTypeEnum.XERO_ERROR, ErrorTypeEnum.XERO_ERROR),
)


class Error(models.Model):
    """
    Table to store errors
    """

    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.PROTECT, help_text="Reference to Workspace model"
    )
    type = models.CharField(
        max_length=50, choices=ERROR_TYPE_CHOICES, help_text="Error type"
    )
    expense_group = models.ForeignKey(
        ExpenseGroup,
        on_delete=models.PROTECT,
        null=True,
        help_text="Reference to Expense group",
    )
    mapping_error_expense_group_ids = ArrayField(base_field=models.IntegerField(), default=[], help_text='list of mapping expense group ids')
    expense_attribute = models.OneToOneField(
        ExpenseAttribute,
        on_delete=models.PROTECT,
        null=True,
        help_text="Reference to Expense Attribute",
    )
    repetition_count = models.IntegerField(help_text='repetition count for the error', default=0)
    is_resolved = models.BooleanField(default=False, help_text="Is resolved")
    error_title = models.CharField(max_length=255, help_text="Error title")
    error_detail = models.TextField(help_text="Error detail")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")

    def increase_repetition_count_by_one(self, is_created: bool):
        """
        Increase the repetition count by 1.
        """
        if not is_created:
            self.repetition_count += 1
            self.save()

    @staticmethod
    def get_or_create_error_with_expense_group(expense_group, expense_attribute):
        """
        Get or create an Error record and ensure that the expense_group.id
        is present in mapping_error_expense_group_ids (without duplicates).
        """
        error_type = get_error_type_mapping(expense_attribute.attribute_type)
        error_detail = f"{expense_attribute.display_name} mapping is missing"

        error, created = Error.objects.get_or_create(
            workspace_id=expense_group.workspace_id,
            expense_attribute=expense_attribute,
            defaults={
                'type': error_type,
                'error_detail': error_detail,
                'error_title': expense_attribute.value,
                'is_resolved': False,
                'mapping_error_expense_group_ids': [expense_group.id],
            }
        )

        if not created and expense_group.id not in error.mapping_error_expense_group_ids:
            error.mapping_error_expense_group_ids = list(set(error.mapping_error_expense_group_ids + [expense_group.id]))
            error.save(update_fields=['mapping_error_expense_group_ids'])
        return error, created

    class Meta:
        db_table = "errors"
