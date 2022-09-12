# Generated by Django 3.1.14 on 2022-09-09 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0024_auto_20220909_1206'),
        ('mappings', '0005_auto_20220329_0837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalmapping',
            name='workspace',
            field=models.OneToOneField(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, related_name='general_mappings', to='workspaces.workspace'),
        ),
    ]
