# Generated by Django 4.2.18 on 2025-02-18 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0023_auto_20250108_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='imported_from',
            field=models.CharField(choices=[('WEBHOOK', 'WEBHOOK'), ('DASHBOARD_SYNC', 'DASHBOARD_SYNC'), ('DIRECT_EXPORT', 'DIRECT_EXPORT'), ('BACKGROUND_SCHEDULE', 'BACKGROUND_SCHEDULE')], help_text='Imported from source', max_length=255, null=True),
        ),
    ]
