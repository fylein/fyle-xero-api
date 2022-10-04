from django.db import models
from django.db.models import JSONField

from apps.workspaces.models import Workspace
from apps.fyle.models import ExpenseGroup
from apps.xero.models import Bill, BankTransaction, Payment
from fyle_accounting_mappings.models import ExpenseAttribute


def get_default():
    return dict


class TaskLog(models.Model):
    """
    Table to store task logs
    """
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    type = models.CharField(max_length=50, help_text='Task type (FETCH_EXPENSES / CREATE_BILL)')
    task_id = models.CharField(max_length=255, null=True, help_text='Django Q task reference')
    expense_group = models.ForeignKey(ExpenseGroup, on_delete=models.PROTECT,
                                      null=True, help_text='Reference to Expense group')
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, help_text='Reference to Payment', null=True)
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, help_text='Reference to Bill', null=True)
    bank_transaction = models.ForeignKey(BankTransaction, on_delete=models.PROTECT,
                                         help_text='Reference to Bank Transaction', null=True)
    status = models.CharField(max_length=255, help_text='Task Status')
    detail = JSONField(help_text='Task response', null=True, default=get_default())
    xero_errors = JSONField(help_text='Xero Errors', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'task_logs'

ERROR_TYPE_CHOICES = (
    ('EMPLOYEE_MAPPING', 'EMPLOYEE_MAPPING'),
    ('CATEGORY_MAPPING', 'CATEGORY_MAPPING'),
    ('XERO_ERROR', 'XERO_ERROR')
)


class Error(models.Model):
    """
    Table to store errors
    """
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    type = models.CharField(max_length=50, choices=ERROR_TYPE_CHOICES, help_text='Error type')
    expense_group = models.ForeignKey(
        ExpenseGroup, on_delete=models.PROTECT, 
        null=True, help_text='Reference to Expense group'
    )
    expense_attribute = models.OneToOneField(
        ExpenseAttribute, on_delete=models.PROTECT,
        null=True, help_text='Reference to Expense Attribute'
    )
    is_resolved = models.BooleanField(default=False, help_text='Is resolved')
    error_title = models.CharField(max_length=255, help_text='Error title')
    error_detail = models.TextField(help_text='Error detail')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'errors'
