# Generated by Django 4.2.18 on 2025-01-21 16:06

from django.db import migrations
from apps.internal.helpers import safe_run_sql


sql_files = ['fyle-integrations-db-migrations/xero/functions/delete_workspace.sql',
             'fyle-integrations-db-migrations/xero/functions/re_export_expenses_xero.sql', 
             'fyle-integrations-db-migrations/xero/functions/trigger_auto_import.sql']

class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0027_auto_20250121_1514'),
    ]

    operations = safe_run_sql(sql_files)
