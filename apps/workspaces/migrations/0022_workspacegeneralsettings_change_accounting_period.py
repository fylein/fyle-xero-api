# Generated by Django 3.1.14 on 2022-07-23 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0021_workspacegeneralsettings_import_customers'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='change_accounting_period',
            field=models.BooleanField(default=False, help_text='Change the accounting period'),
        ),
    ]
