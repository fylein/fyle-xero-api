# Generated by Django 3.2.14 on 2024-03-20 07:23

import apps.workspaces.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0037_workspacegeneralsettings_import_suppliers_as_merchants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workspace',
            name='onboarding_state',
            field=models.CharField(choices=[('CONNECTION', 'CONNECTION'), ('TENANT_MAPPING', 'TENANT_MAPPING'), ('EXPORT_SETTINGS', 'EXPORT_SETTINGS'), ('IMPORT_SETTINGS', 'IMPORT_SETTINGS'), ('ADVANCED_CONFIGURATION', 'ADVANCED_CONFIGURATION'), ('COMPLETE', 'COMPLETE')], default=apps.workspaces.models.get_default_onboarding_state, help_text='Onboarding status of the workspace', max_length=50, null=True),
        ),
    ]