# Generated by Django 3.0.3 on 2021-02-01 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mappings', '0002_generalmapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalmapping',
            name='payment_account_id',
            field=models.CharField(help_text='Xero payment account id', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='generalmapping',
            name='payment_account_name',
            field=models.CharField(help_text='Xero Payment Account name', max_length=255, null=True),
        ),
    ]