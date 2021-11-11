# Generated by Django 3.0.3 on 2021-10-25 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0006_expense_file_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='corporate_card_id',
            field=models.CharField(blank=True, help_text='Corporate Card ID', max_length=255, null=True),
        ),
    ]
