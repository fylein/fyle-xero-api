# Generated by Django 3.1.14 on 2022-06-14 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0019_workspacegeneralsettings_charts_of_accounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='import_customers',
            field=models.BooleanField(default=False, help_text='Auto import customers to Fyle'),
        ),
    ]
