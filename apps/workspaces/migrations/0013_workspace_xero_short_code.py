# Generated by Django 3.0.3 on 2021-11-29 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0012_workspacegeneralsettings_map_fyle_cards_xero_bank_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspace',
            name='xero_short_code',
            field=models.CharField(blank=True, help_text='Xero short code', max_length=30, null=True),
        ),
    ]
