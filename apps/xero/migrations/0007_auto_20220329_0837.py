# Generated by Django 3.1.14 on 2022-03-29 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xero', '0006_auto_20211206_0733'),
    ]

    operations = [
        migrations.AddField(
            model_name='billlineitem',
            name='tax_amount',
            field=models.FloatField(help_text='Tax amount', null=True),
        ),
        migrations.AddField(
            model_name='billlineitem',
            name='tax_code',
            field=models.CharField(help_text='Tax Group ID', max_length=255, null=True),
        ),
    ]
