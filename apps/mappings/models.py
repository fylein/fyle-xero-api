"""
Mapping Models
"""
from django.db import models

from apps.workspaces.models import Workspace


class TenantMapping(models.Model):
    """
    Tenant Mapping
    """

    id = models.AutoField(primary_key=True)
    tenant_name = models.CharField(max_length=255, help_text="Xero Tenant name")
    tenant_id = models.CharField(max_length=255, help_text="Xero Tenant id")
    connection_id = models.CharField(
        max_length=255, help_text="Xero Connection id", null=True, blank=True
    )
    workspace = models.OneToOneField(
        Workspace, on_delete=models.PROTECT, help_text="Reference to Workspace model"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")

    class Meta:
        unique_together = ("tenant_name", "workspace")
        db_table = "tenant_mappings"

    @staticmethod
    def get_tenant_details(workspace_id):
        return TenantMapping.objects.get(workspace_id=workspace_id)


class GeneralMapping(models.Model):
    """
    General Mapping
    """

    id = models.AutoField(primary_key=True)
    bank_account_name = models.CharField(
        max_length=255, help_text="Xero bank account name", null=True
    )
    bank_account_id = models.CharField(
        max_length=255, help_text="Xero bank account id", null=True
    )
    payment_account_name = models.CharField(
        max_length=255, help_text="Xero Payment Account name", null=True
    )
    payment_account_id = models.CharField(
        max_length=255, help_text="Xero payment account id", null=True
    )
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.PROTECT,
        help_text="Reference to Workspace model",
        related_name="general_mappings",
    )
    default_tax_code_name = models.CharField(
        max_length=255, help_text="Xero default Tax Code name", null=True
    )
    default_tax_code_id = models.CharField(
        max_length=255, help_text="Xero default Tax Code ID", null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Created at datetime"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at datetime")

    class Meta:
        unique_together = ("bank_account_name", "workspace")
        db_table = "general_mappings"
