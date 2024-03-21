# Generated by Django 3.1.14 on 2023-09-22 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fyle_accounting_mappings', '0023_auto_20230918_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorymapping',
            name='source_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='categorymapping', to='fyle_accounting_mappings.expenseattribute'),
        ),
        migrations.AlterField(
            model_name='mapping',
            name='destination',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='mapping', to='fyle_accounting_mappings.destinationattribute'),
        ),
    ]
