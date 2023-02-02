# Generated by Django 3.1.14 on 2023-01-19 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0031_auto_20221116_0649'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='is_simplify_report_closure_enabled',
            field=models.BooleanField(default=False, help_text='Simplify report closure is enabled'),
        ),
    ]