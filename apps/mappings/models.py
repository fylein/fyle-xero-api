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
    tenant_name = models.CharField(max_length=255, help_text='Xero Tenant name')
    tenant_id = models.CharField(max_length=255, help_text='Xero Tenant id')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('tenant_name', 'workspace')
        db_table = 'tenant_mappings'
