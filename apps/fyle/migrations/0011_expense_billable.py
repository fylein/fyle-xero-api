# Generated by Django 3.1.14 on 2022-06-15 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0010_auto_20220329_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='billable',
            field=models.BooleanField(default=False, help_text='Expense billable or not'),
        ),
    ]