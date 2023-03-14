# Generated by Django 3.1.14 on 2023-03-14 05:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0033_auto_20230314_0156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workspaceschedule',
            name='workspace',
            field=models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, related_name='workspace_schedules', to='workspaces.workspace'),
        ),
    ]
