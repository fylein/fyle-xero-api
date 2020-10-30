# Generated by Django 3.0.3 on 2020-10-30 05:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.AutoField(help_text='Unique Id to identify a workspace', primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name of the workspace', max_length=255)),
                ('fyle_org_id', models.CharField(help_text='Xero Tenant ID', max_length=255, unique=True)),
                ('xero_tenant_id', models.CharField(help_text='org id', max_length=255, unique=True)),
                ('last_synced_at', models.DateTimeField(help_text='Datetime when expenses were pulled last', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at datetime')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at datetime')),
                ('user', models.ManyToManyField(help_text='Reference to users table', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'workspaces',
            },
        ),
        migrations.CreateModel(
            name='XeroCredentials',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('refresh_token', models.TextField(help_text='Stores Xero refresh token')),
                ('tenant_id', models.TextField(help_text='Stores Xero Tenant ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at datetime')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at datetime')),
                ('workspace', models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, to='workspaces.Workspace')),
            ],
            options={
                'db_table': 'xero_credentials',
            },
        ),
        migrations.CreateModel(
            name='WorkspaceGeneralSettings',
            fields=[
                ('id', models.AutoField(help_text='Unique Id to identify a workspace', primary_key=True, serialize=False)),
                ('reimbursable_expenses_object', models.CharField(help_text='Reimbursable Expenses type', max_length=50)),
                ('corporate_credit_card_expenses_object', models.CharField(help_text='Non Reimbursable Expenses type', max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at')),
                ('workspace', models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, to='workspaces.Workspace')),
            ],
        ),
        migrations.CreateModel(
            name='FyleCredential',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('refresh_token', models.TextField(help_text='Stores Fyle refresh token')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at datetime')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at datetime')),
                ('workspace', models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, to='workspaces.Workspace')),
            ],
            options={
                'db_table': 'fyle_credentials',
            },
        ),
    ]
