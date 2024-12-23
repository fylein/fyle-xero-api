# Generated by Django 3.2.14 on 2024-12-23 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0040_workspacegeneralsettings_memo_structure'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspaceschedule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Created at datetime', null=True),
        ),
        migrations.AddField(
            model_name='workspaceschedule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text='Updated at datetime', null=True),
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE workspaces_user
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
            """,
            reverse_sql="""
                ALTER TABLE workspaces_user
                DROP COLUMN created_at;
            """,
        ),
    ]
