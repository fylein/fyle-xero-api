# Generated by Django 3.0.3 on 2020-11-02 17:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0001_initial'),
        ('xero', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('contact_id', models.CharField(help_text='Xero Contact ID', max_length=255)),
                ('bank_account_code', models.CharField(help_text='Xero Bank Account code', max_length=255)),
                ('currency', models.CharField(help_text='Bank Transaction Currency', max_length=255)),
                ('reference', models.CharField(help_text='Bank Transaction ID', max_length=255)),
                ('transaction_date', models.DateField(help_text='Bank transaction date')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at')),
                ('expense_group', models.OneToOneField(help_text='Expense group reference', on_delete=django.db.models.deletion.PROTECT, to='fyle.ExpenseGroup')),
            ],
        ),
        migrations.CreateModel(
            name='BankTransactionLineItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('account_id', models.CharField(help_text='Xero AccountCode', max_length=255)),
                ('item_code', models.CharField(help_text='Xero ItemCode', max_length=255, null=True)),
                ('tracking_categories', django.contrib.postgres.fields.jsonb.JSONField(help_text='Save Tracking options', null=True)),
                ('amount', models.FloatField(help_text='Bank Transaction LineAmount')),
                ('description', models.CharField(help_text='Xero Bank Transaction LineItem description', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at')),
                ('bank_transaction', models.ForeignKey(help_text='Reference to bank transaction', on_delete=django.db.models.deletion.PROTECT, to='xero.BankTransaction')),
                ('expense', models.OneToOneField(help_text='Reference to Expense', on_delete=django.db.models.deletion.PROTECT, to='fyle.Expense')),
            ],
        ),
    ]
