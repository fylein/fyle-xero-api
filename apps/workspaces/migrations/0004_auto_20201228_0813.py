# Generated by Django 3.0.3 on 2020-12-28 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0003_workspaceschedule'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='workspacegeneralsettings',
            table='workspace_general_settings',
        ),
        migrations.AlterModelTable(
            name='workspaceschedule',
            table='workspace_schedules',
        ),
    ]