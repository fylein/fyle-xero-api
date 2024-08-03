# Generated by Django 3.2.14 on 2024-08-03 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0019_expense_paid_on_fyle'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensegroup',
            name='export_url',
            field=models.CharField(help_text='Netsuite URL for the exported expenses', max_length=255, null=True),
        ),
    ]
