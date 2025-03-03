from django.db import models
from django.db.models import JSONField
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_accounting_library.fyle_platform.constants import IMPORTED_FROM_CHOICES

from apps.fyle.models import ExpenseGroup
from apps.tasks.enums import ErrorTypeEnum
from apps.workspaces.models import Workspace
from apps.xero.models import BankTransaction, Bill, Payment


def get_default():
    return dict


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

    class Meta:
        db_table = "errors"
