"""
Workspace Models
"""
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField
from django_q.models import Schedule
from fyle_accounting_mappings.mixins import AutoAddCreateUpdateInfoMixin

User = get_user_model()

ONBOARDING_STATE_CHOICES = (
    ('CONNECTION', 'CONNECTION'),
    ('TENANT_MAPPING', 'TENANT_MAPPING'),
    ('EXPORT_SETTINGS', 'EXPORT_SETTINGS'),
    ('IMPORT_SETTINGS', 'IMPORT_SETTINGS'),
    ('ADVANCED_CONFIGURATION', 'ADVANCED_CONFIGURATION'),
    ('COMPLETE', 'COMPLETE')
)

# add or remove this after discussion.
AUTO_MAP_EMPLOYEE = (
    ("EMAIL", "EMAIL"),
    ("NAME", "NAME"),
    ("EMPLOYEE_CODE", "EMPLOYEE_CODE"),
)

APP_VERSION_CHOICES = (("v1", "v1"), ("v2", "v2"))

EXPORT_MODE_CHOICES = (("MANUAL", "MANUAL"), ("AUTO", "AUTO"))


def get_default_memo_fields():
    return ['employee_email', 'category', 'merchant', 'spent_on', 'report_number', 'purpose']


def get_default_chart_of_accounts():
    return ["EXPENSE"]


def get_default_onboarding_state():
    return "CONNECTION"


class Workspace(models.Model):
    """
    Workspace model
    """

    id = models.AutoField(
        primary_key=True, help_text="Unique Id to identify a workspace"
    )
    name = models.CharField(max_length=255, help_text="Name of the workspace")
    user = models.ManyToManyField(User, help_text="Reference to users table")
    fyle_org_id = models.CharField(max_length=255, help_text="org id", unique=True)
    fyle_currency = models.CharField(max_length=5, help_text="Fyle Currency", null=True)
    xero_currency = models.CharField(max_length=5, help_text="Xero Currency", null=True)
    app_version = models.CharField(
        max_length=2, help_text="App version", default="v2", choices=APP_VERSION_CHOICES
    )
    xero_short_code = models.CharField(
        max_length=30, help_text="Xero short code", null=True, blank=True
    )
    last_synced_at = models.DateTimeField(
        help_text="Datetime when expenses were pulled last", null=True
    )
    ccc_last_synced_at = models.DateTimeField(
        help_text="Datetime when ccc expenses were pulled last", null=True
    )
    source_synced_at = models.DateTimeField(
        help_text="Datetime when source dimensions were pulled", null=True
    )
    destination_synced_at = models.DateTimeField(
        help_text="Datetime when destination dimensions were pulled", null=True
    )
    onboarding_state = models.CharField(
        max_length=50,
        choices=ONBOARDING_STATE_CHOICES,
        default=get_default_onboarding_state,
        help_text="Onboarding status of the workspace",
        null=True,
    )
    xero_accounts_last_synced_at = models.DateTimeField(
        null=True, help_text="Xero Accounts last synced at time"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")

    class Meta:
        db_table = "workspaces"


class XeroCredentials(models.Model):
    """
    Table to store Xero credentials
    """

    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text="Stores Xero refresh token", null=True)
    workspace = models.OneToOneField(
        Workspace, on_delete=models.PROTECT, help_text="Reference to Workspace model"
    )
    is_expired = models.BooleanField(default=False, help_text="Xero token expiry flag")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")
    country = models.CharField(max_length=255, help_text="Xero Country Name", null=True)

    class Meta:
        db_table = "xero_credentials"

    @staticmethod
    def get_active_xero_credentials(workspace_id):
        return XeroCredentials.objects.get(
            workspace_id=workspace_id, is_expired=False, refresh_token__isnull=False
        )

    @staticmethod
    def get_xero_credentials(workspace_id):
        return XeroCredentials.objects.filter(workspace_id=workspace_id).first()


class FyleCredential(models.Model):
    """
    Table to store Fyle credentials
    """

    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text="Stores Fyle refresh token")
    cluster_domain = models.CharField(
        max_length=255, help_text="Cluster domain", null=True
    )
    workspace = models.OneToOneField(
        Workspace, on_delete=models.PROTECT, help_text="Reference to Workspace model"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")

    class Meta:
        db_table = "fyle_credentials"


class WorkspaceGeneralSettings(AutoAddCreateUpdateInfoMixin, models.Model):
    """
    Workspace General Settings
    """

    id = models.AutoField(
        primary_key=True, help_text="Unique Id to identify a workspace"
    )
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.PROTECT,
        help_text="Reference to Workspace model",
        related_name="workspace_general_settings",
    )
    reimbursable_expenses_object = models.CharField(
        max_length=50, help_text="Reimbursable Expenses type", null=True
    )
    corporate_credit_card_expenses_object = models.CharField(
        max_length=50, help_text="Non Reimbursable Expenses type", null=True
    )
    sync_fyle_to_xero_payments = models.BooleanField(
        default=False, help_text="Auto Sync Payments from Fyle to Xero"
    )
    sync_xero_to_fyle_payments = models.BooleanField(
        default=False, help_text="Auto Sync Payments from Xero to Fyle"
    )
    map_merchant_to_contact = models.BooleanField(
        default=False, help_text="Map Merchant to Contact for CCC Expenses"
    )
    change_accounting_period = models.BooleanField(
        default=True, help_text="Change the accounting period"
    )
    import_categories = models.BooleanField(
        default=False, help_text="Auto import Categories to Fyle"
    )
    auto_map_employees = models.CharField(
        max_length=50,
        help_text="Auto Map Employees from Xero to Fyle",
        null=True,
        choices=AUTO_MAP_EMPLOYEE,
    )
    memo_structure = ArrayField(
        base_field=models.CharField(max_length=100), default=get_default_memo_fields,
        help_text='list of system fields for creating custom memo'
    )

    auto_create_destination_entity = models.BooleanField(
        default=False, help_text="Auto create contact"
    )
    auto_create_merchant_destination_entity = models.BooleanField(
        default=False, help_text="Auto create fyle merchnat as xero contact"
    )
    import_tax_codes = models.BooleanField(
        default=False, help_text="Auto import tax codes to Fyle", null=True
    )
    import_customers = models.BooleanField(
        default=False, help_text="Auto import customers to Fyle"
    )
    import_suppliers_as_merchants = models.BooleanField(
        default=False, help_text="Auto import suppliers to Fyle"
    )
    skip_accounting_export_summary_post = models.BooleanField(
        default=False, help_text="Skip posting accounting export summary"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")
    charts_of_accounts = ArrayField(
        base_field=models.CharField(max_length=100),
        default=get_default_chart_of_accounts,
        help_text="list of chart of account types to be imported into Fyle",
    )

    class Meta:
        db_table = "workspace_general_settings"


class WorkspaceSchedule(models.Model):
    """
    Workspace Schedule
    """

    id = models.AutoField(
        primary_key=True, help_text="Unique Id to identify a schedule"
    )
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.PROTECT,
        help_text="Reference to Workspace model",
        related_name="workspace_schedules",
    )
    enabled = models.BooleanField(default=False)
    start_datetime = models.DateTimeField(
        help_text="Datetime for start of schedule", null=True
    )
    is_real_time_export_enabled = models.BooleanField(default=False)
    interval_hours = models.IntegerField(null=True)
    schedule = models.OneToOneField(Schedule, on_delete=models.PROTECT, null=True)
    error_count = models.IntegerField(null=True, help_text="Number of errors in export")
    additional_email_options = JSONField(
        default=list, help_text="Email and Name of person to send email", null=True
    )
    emails_selected = ArrayField(
        base_field=models.CharField(max_length=255),
        null=True,
        help_text="Emails that has to be send mail",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, null=True, help_text='Updated at datetime')

    class Meta:
        db_table = "workspace_schedules"


class LastExportDetail(models.Model):
    """
    Table to store Last Export Details
    """

    id = models.AutoField(primary_key=True)
    last_exported_at = models.DateTimeField(
        help_text="Last exported at datetime", null=True
    )
    export_mode = models.CharField(
        max_length=50,
        help_text="Mode of the export Auto / Manual",
        choices=EXPORT_MODE_CHOICES,
        null=True,
    )
    total_expense_groups_count = models.IntegerField(
        help_text="Total count of expense groups exported", null=True
    )
    successful_expense_groups_count = models.IntegerField(
        help_text="count of successful expense_groups ", null=True
    )
    failed_expense_groups_count = models.IntegerField(
        help_text="count of failed expense_groups ", null=True
    )
    workspace = models.OneToOneField(
        Workspace, on_delete=models.PROTECT, help_text="Reference to Workspace model"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")

    class Meta:
        db_table = "last_export_details"
