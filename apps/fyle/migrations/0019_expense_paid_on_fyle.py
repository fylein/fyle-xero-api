# Generated by Django 3.2.14 on 2024-06-18 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0018_auto_20240213_0450'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='paid_on_fyle',
            field=models.BooleanField(default=False, help_text='Expense Payment status on Fyle'),
        ),
    ]
