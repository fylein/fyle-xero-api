# Generated by Django 3.0.3 on 2021-02-01 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0004_auto_20201228_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='sync_fyle_to_xero_payments',
            field=models.BooleanField(default=False, help_text='Auto Sync Payments from Fyle to Xero'),
        ),
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='sync_xero_to_fyle_payments',
            field=models.BooleanField(default=False, help_text='Auto Sync Payments from Xero to Fyle'),
        ),
    ]
