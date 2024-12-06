# Generated by Django 3.2.14 on 2024-12-03 10:44

import apps.workspaces.models
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0039_alter_workspacegeneralsettings_change_accounting_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='memo_structure',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=apps.workspaces.models.get_default_memo_fields, help_text='list of system fields for creating custom memo', size=None),
        ),
    ]