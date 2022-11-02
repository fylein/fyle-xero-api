# Generated by Django 3.1.14 on 2022-11-02 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mappings', '0006_auto_20220909_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenantmapping',
            name='tenant_id',
            field=models.CharField(help_text='Xero Tenant id', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tenantmapping',
            name='tenant_name',
            field=models.CharField(help_text='Xero Tenant name', max_length=255, null=True),
        ),
    ]
