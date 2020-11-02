# Generated by Django 3.0.3 on 2020-11-02 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xero', '0002_banktransaction_banktransactionlineitem'),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklog',
            name='bank_transaction',
            field=models.ForeignKey(help_text='Reference to Bank Transaction', null=True, on_delete=django.db.models.deletion.PROTECT, to='xero.BankTransaction'),
        ),
        migrations.AddField(
            model_name='tasklog',
            name='bill',
            field=models.ForeignKey(help_text='Reference to Bill', null=True, on_delete=django.db.models.deletion.PROTECT, to='xero.Bill'),
        ),
    ]