# Generated by Django 3.1.14 on 2022-11-02 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0029_workspace_ccc_last_synced_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='xerocredentials',
            name='is_expired',
            field=models.BooleanField(default=False, help_text='Xero token expiry flag'),
        ),
        migrations.AlterField(
            model_name='xerocredentials',
            name='refresh_token',
            field=models.TextField(help_text='Stores Xero refresh token', null=True),
        ),
    ]
