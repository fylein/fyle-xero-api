# Generated by Django 3.1.14 on 2023-08-24 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0036_auto_20230323_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacegeneralsettings',
            name='import_suppliers_as_merchants',
            field=models.BooleanField(default=False, help_text='Auto import suppliers to Fyle'),
        ),
    ]
