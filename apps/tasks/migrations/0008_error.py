# Generated by Django 3.1.14 on 2022-10-04 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fyle', '0012_auto_20220923_0613'),
        ('workspaces', '0026_auto_20221004_1922'),
        ('fyle_accounting_mappings', '0018_auto_20220419_0709'),
        ('tasks', '0007_auto_20211206_0733'),
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('EMPLOYEE_MAPPING', 'EMPLOYEE_MAPPING'), ('CATEGORY_MAPPING', 'CATEGORY_MAPPING'), ('XERO_ERROR', 'XERO_ERROR')], help_text='Error type', max_length=50)),
                ('is_resolved', models.BooleanField(default=False, help_text='Is resolved')),
                ('error_title', models.CharField(help_text='Error title', max_length=255)),
                ('error_detail', models.TextField(help_text='Error detail')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at datetime')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at datetime')),
                ('expense_attribute', models.OneToOneField(help_text='Reference to Expense Attribute', null=True, on_delete=django.db.models.deletion.PROTECT, to='fyle_accounting_mappings.expenseattribute')),
                ('expense_group', models.ForeignKey(help_text='Reference to Expense group', null=True, on_delete=django.db.models.deletion.PROTECT, to='fyle.expensegroup')),
                ('workspace', models.ForeignKey(help_text='Reference to Workspace model', on_delete=django.db.models.deletion.PROTECT, to='workspaces.workspace')),
            ],
            options={
                'db_table': 'errors',
            },
        ),
    ]
