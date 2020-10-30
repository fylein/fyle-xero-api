"""
Workspace Models
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Workspace(models.Model):
    """
    Workspace model
    """
    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')
    name = models.CharField(max_length=255, help_text='Name of the workspace')
    user = models.ManyToManyField(User, help_text='Reference to users table')
    fyle_org_id = models.CharField(max_length=255, help_text='org id', unique=True)
    last_synced_at = models.DateTimeField(help_text='Datetime when expenses were pulled last', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'workspaces'


class XeroCredentials(models.Model):
    """
    Table to store Xero credentials
    """
    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text='Stores Xero refresh token')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'xero_credentials'


class FyleCredential(models.Model):
    """
    Table to store Fyle credentials
    """
    id = models.AutoField(primary_key=True)
    refresh_token = models.TextField(help_text='Stores Fyle refresh token')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'fyle_credentials'


class WorkspaceGeneralSettings(models.Model):
    """
    Workspace General Settings
    """
    id = models.AutoField(primary_key=True, help_text='Unique Id to identify a workspace')
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    reimbursable_expenses_object = models.CharField(max_length=50, help_text='Reimbursable Expenses type')
    corporate_credit_card_expenses_object = models.CharField(max_length=50,
                                                             help_text='Non Reimbursable Expenses type', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at')
