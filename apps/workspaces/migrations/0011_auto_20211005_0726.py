# Generated by Django 3.0.3 on 2021-09-28 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0010_auto_20210414_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='fylecredential',
            name='cluster_domain',
            field=models.CharField(help_text='Cluster domain', max_length=255, null=True),
        ),
    ]