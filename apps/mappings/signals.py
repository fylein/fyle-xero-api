"""
Mappings Signal
"""


from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_q.tasks import async_task
from fyle_accounting_mappings.models import Mapping, MappingSetting

from apps.mappings.helpers import schedule_or_delete_fyle_import_tasks
from apps.mappings.models import TenantMapping
from apps.mappings.queue import schedule_cost_centers_creation, schedule_fyle_attributes_creation
from apps.mappings.tasks import upload_attributes_to_fyle
from apps.tasks.models import Error
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.fyle.enums import FyleAttributeEnum


@receiver(post_save, sender=Mapping)
def resolve_post_mapping_errors(sender, instance: Mapping, **kwargs):
    """
    Resolve errors after mapping is created
    """
    if instance.source_type in (FyleAttributeEnum.CATEGORY, FyleAttributeEnum.EMPLOYEE):
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
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(
        workspace_id=instance.workspace_id
    ).first()
    if instance.source_field == FyleAttributeEnum.PROJECT:
        schedule_or_delete_fyle_import_tasks(workspace_general_settings)

    if instance.source_field == FyleAttributeEnum.COST_CENTER:
        schedule_cost_centers_creation(
            instance.import_to_fyle, int(instance.workspace_id)
        )

    if instance.is_custom:
        schedule_fyle_attributes_creation(int(instance.workspace_id))


@receiver(pre_save, sender=MappingSetting)
def run_pre_mapping_settings_triggers(sender, instance: MappingSetting, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row instance of Sender Class
    :return: None
    """
    default_attributes = [
        FyleAttributeEnum.EMPLOYEE,
        FyleAttributeEnum.CATEGORY,
        FyleAttributeEnum.PROJECT,
        FyleAttributeEnum.COST_CENTER,
        FyleAttributeEnum.CORPORATE_CARD,
        FyleAttributeEnum.TAX_GROUP
    ]

    instance.source_field = instance.source_field.upper().replace(" ", "_")

    if instance.source_field not in default_attributes:
        upload_attributes_to_fyle(
            workspace_id=int(instance.workspace_id),
            xero_attribute_type=instance.destination_field,
            fyle_attribute_type=instance.source_field,
            source_placeholder=instance.source_placeholder,
        )

        async_task(
            "apps.mappings.tasks.auto_create_expense_fields_mappings",
            int(instance.workspace_id),
            instance.destination_field,
            instance.source_field,
            q_options={
                'cluster': 'import'
            }
        )


@receiver(post_save, sender=TenantMapping)
def run_post_tenant_mapping_trigger(sender, instance: TenantMapping, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_task("apps.xero.tasks.create_missing_currency", int(instance.workspace_id), q_options={ 'cluster': 'import' })
    async_task("apps.xero.tasks.update_xero_short_code", int(instance.workspace_id), q_options={ 'cluster': 'import' })
