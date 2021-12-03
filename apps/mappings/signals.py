"""
Mappings Signal
"""
from django.db.models import Q
from django.db.models.signals import post_save, pre_save

from django.dispatch import receiver
from datetime import datetime

from django_q.tasks import async_task

from fyle_accounting_mappings.models import MappingSetting, ExpenseAttribute
from apps.mappings.tasks import schedule_projects_creation, schedule_cost_centers_creation, schedule_fyle_attributes_creation,\
                        upload_attributes_to_fyle

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TenantMapping

@receiver(post_save, sender=MappingSetting)
def run_post_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row instance of Sender Class
    :return: None
    """
    if instance.source_field == 'PROJECT':
        schedule_projects_creation(instance.import_to_fyle, int(instance.workspace_id))

    if instance.source_field == 'COST_CENTER':
        schedule_cost_centers_creation(instance.import_to_fyle, int(instance.workspace_id))

    if instance.is_custom:
        schedule_fyle_attributes_creation(int(instance.workspace_id))


@receiver(pre_save, sender=MappingSetting)
def run_pre_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row instance of Sender Class
    :return: None
    """
    default_attributes = ['EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER']

    instance.source_field = instance.source_field.upper().replace(' ', '_')

    if instance.source_field not in default_attributes:
        upload_attributes_to_fyle(
            workspace_id=int(instance.workspace_id),
            xero_attribute_type=instance.destination_field,
            fyle_attribute_type=instance.source_field
        )

        async_task(
            'apps.mappings.tasks.auto_create_expense_fields_mappings',
            int(instance.workspace_id),
            instance.destination_field,
            instance.source_field
        )

@receiver(post_save, sender=TenantMapping)
def run_post_tenant_mapping_trigger(sender, instance: TenantMapping, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_task('apps.xero.tasks.create_missing_currency', int(instance.workspace_id))
    async_task('apps.xero.tasks.update_xero_short_code', int(instance.workspace_id))
