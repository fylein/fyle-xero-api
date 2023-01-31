"""
Mappings Signal
"""
from django.db.models import Q
from django.db.models.signals import post_save, pre_save

from django.dispatch import receiver
from datetime import datetime

from django_q.tasks import async_task

from fyle_accounting_mappings.models import MappingSetting, ExpenseAttribute, Mapping
from apps.tasks.models import Error
from apps.mappings.tasks import schedule_projects_creation, schedule_cost_centers_creation, schedule_fyle_attributes_creation,\
                        upload_attributes_to_fyle
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.workspaces.utils import delete_cards_mapping_settings
from apps.fyle.models import ExpenseGroupSettings

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TenantMapping

@receiver(post_save, sender=Mapping)
def resolve_post_mapping_errors(sender, instance: Mapping, **kwargs):
    """
    Resolve errors after mapping is created
    """
    if instance.source_type in ('CATEGORY', 'EMPLOYEE'):
        error = Error.objects.filter(expense_attribute_id=instance.source_id).first()
        if error:
            error.is_resolved = True
            error.save()

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

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=instance.workspace_id).first()
    expense_group_settings = ExpenseGroupSettings.objects.filter(workspace_id=instance.workspace_id).first()
    if workspace_general_settings:
        delete_cards_mapping_settings(workspace_general_settings, expense_group_settings)


@receiver(pre_save, sender=MappingSetting)
def run_pre_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row instance of Sender Class
    :return: None
    """
    default_attributes = ['EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER', 'CORPORATE_CARD', 'TAX_GROUP']

    instance.source_field = instance.source_field.upper().replace(' ', '_')

    if instance.source_field not in default_attributes:
        upload_attributes_to_fyle(
            workspace_id=int(instance.workspace_id),
            xero_attribute_type=instance.destination_field,
            fyle_attribute_type=instance.source_field,
            source_placeholder=instance.source_placeholder
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
