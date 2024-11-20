# Generated by Django 3.2.14 on 2024-11-20 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0022_support_split_expense_grouping'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='masked_corporate_card_number',
            field=models.CharField(help_text='Masked Corporate Card Number', max_length=255, null=True),
        ),
    ]
