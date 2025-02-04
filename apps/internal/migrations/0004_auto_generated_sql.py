# Generated by Django

from django.db import migrations
from apps.internal.helpers import safe_run_sql

sql_files = [
    'fyle-integrations-db-migrations/common/global_shared/functions/ws_email.sql'
]


class Migration(migrations.Migration):

    dependencies = [('internal', '0003_auto_generated_sql')]

    operations = safe_run_sql(sql_files)
