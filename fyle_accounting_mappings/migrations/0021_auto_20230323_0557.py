# Generated by Django 3.1.14 on 2023-03-23 05:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fyle_accounting_mappings', '0020_auto_20230302_0519'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='expensefield',
            unique_together={('attribute_type', 'workspace_id')},
        ),
    ]
