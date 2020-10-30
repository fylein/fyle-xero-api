# Generated by Django 3.0.3 on 2020-10-30 05:40

import apps.fyle.models
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_email', models.EmailField(help_text='Email id of the Fyle employee', max_length=255)),
                ('category', models.CharField(blank=True, help_text='Fyle Expense Category', max_length=255, null=True)),
                ('sub_category', models.CharField(blank=True, help_text='Fyle Expense Sub-Category', max_length=255, null=True)),
                ('project', models.CharField(blank=True, help_text='Project', max_length=255, null=True)),
                ('expense_id', models.CharField(help_text='Expense ID', max_length=255, unique=True)),
                ('expense_number', models.CharField(help_text='Expense Number', max_length=255)),
                ('claim_number', models.CharField(help_text='Claim Number', max_length=255, null=True)),
                ('amount', models.FloatField(help_text='Home Amount')),
                ('currency', models.CharField(help_text='Home Currency', max_length=5)),
                ('foreign_amount', models.FloatField(help_text='Foreign Amount', null=True)),
                ('foreign_currency', models.CharField(help_text='Foreign Currency', max_length=5, null=True)),
                ('settlement_id', models.CharField(help_text='Settlement ID', max_length=255, null=True)),
                ('reimbursable', models.BooleanField(default=False, help_text='Expense reimbursable or not')),
                ('exported', models.BooleanField(default=False, help_text='Expense exported or not')),
                ('state', models.CharField(help_text='Expense state', max_length=255)),
                ('vendor', models.CharField(blank=True, help_text='Vendor', max_length=255, null=True)),
                ('cost_center', models.CharField(blank=True, help_text='Fyle Expense Cost Center', max_length=255, null=True)),
                ('purpose', models.TextField(blank=True, help_text='Purpose', null=True)),
                ('report_id', models.CharField(help_text='Report ID', max_length=255)),
                ('spent_at', models.DateTimeField(help_text='Expense spent at', null=True)),
                ('approved_at', models.DateTimeField(help_text='Expense approved at', null=True)),
                ('expense_created_at', models.DateTimeField(help_text='Expense created at')),
                ('expense_updated_at', models.DateTimeField(help_text='Expense created at')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at')),
                ('fund_source', models.CharField(help_text='Expense fund source', max_length=255)),
                ('verified_at', models.DateTimeField(help_text='Report verified at', null=True)),
                ('custom_properties', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
            ],
            options={
                'db_table': 'expenses',
            },
        ),
        migrations.CreateModel(
            name='ExpenseGroupSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reimbursable_expense_group_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=apps.fyle.models.get_default_expense_group_fields, help_text='list of fields reimbursable expense grouped by', size=None)),
                ('corporate_credit_card_expense_group_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=apps.fyle.models.get_default_expense_group_fields, help_text='list of fields ccc expenses grouped by', size=None)),
                ('expense_state', models.CharField(default=apps.fyle.models.get_default_expense_state, help_text='state at which the expenses are fetched ( PAYMENT_PENDING / PAYMENT_PROCESSING / PAID)', max_length=100)),
                ('export_date_type', models.CharField(default='current_date', help_text='Export Date', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at')),
                ('workspace', models.OneToOneField(help_text='To which workspace this expense group setting belongs to', on_delete=django.db.models.deletion.PROTECT, to='workspaces.Workspace')),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fund_source', models.CharField(help_text='Expense fund source', max_length=255)),
                ('description', django.contrib.postgres.fields.jsonb.JSONField(help_text='Description', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at')),
                ('exported_at', models.DateTimeField(help_text='Exported at', null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at')),
                ('expenses', models.ManyToManyField(help_text='Expenses under this Expense Group', to='fyle.Expense')),
                ('workspace', models.ForeignKey(help_text='To which workspace this expense group belongs to', on_delete=django.db.models.deletion.PROTECT, to='workspaces.Workspace')),
            ],
            options={
                'db_table': 'expense_groups',
            },
        ),
    ]
