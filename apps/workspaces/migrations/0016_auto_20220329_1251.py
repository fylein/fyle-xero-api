# Generated by Django 3.1.14 on 2022-03-29 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0015_auto_20220329_0837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='xerocredentials',
            name='company_name',
        ),
        migrations.RemoveField(
            model_name='xerocredentials',
            name='country',
        ),
    ]