# Generated by Django 3.0.3 on 2020-12-21 08:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_tasklog_xero_errors'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='tasklog',
            table='task_logs',
        ),
    ]