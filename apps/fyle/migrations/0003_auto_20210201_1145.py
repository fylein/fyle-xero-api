# Generated by Django 3.0.3 on 2021-02-01 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0005_auto_20210201_1145'),
        ('fyle', '0002_auto_20201221_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='paid_on_xero',
            field=models.BooleanField(default=False, help_text='Expense Payment status on Xero'),
        ),
        migrations.CreateModel(
            name='Reimbursement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('settlement_id', models.CharField(help_text='Fyle Settlement ID', max_length=255)),
                ('reimbursement_id', models.CharField(help_text='Fyle Reimbursement ID', max_length=255)),
                ('state', models.CharField(help_text='Fyle Reimbursement State', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Updated at')),
                ('workspace', models.ForeignKey(help_text='To which workspace this reimbursement belongs to', on_delete=django.db.models.deletion.PROTECT, to='workspaces.Workspace')),
            ],
            options={
                'db_table': 'reimbursements',
            },
        ),
    ]