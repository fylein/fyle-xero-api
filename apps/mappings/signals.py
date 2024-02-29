"""
Mappings Signal
"""


from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_q.tasks import Chain, async_task
from fyle_accounting_mappings.models import Mapping, MappingSetting

from apps.fyle.enums import FyleAttributeEnum
from apps.mappings.models import TenantMapping
from apps.tasks.models import Error
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.mappings.schedules import new_schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import XeroCredentials
from apps.mappings.constants import SYNC_METHODS
from apps.mappings.helpers import is_auto_sync_allowed


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

    ALLOWED_SOURCE_FIELDS = [
        FyleAttributeEnum.PROJECT,
        FyleAttributeEnum.COST_CENTER,
    ]

    if instance.source_field in ALLOWED_SOURCE_FIELDS or instance.is_custom:
        new_schedule_or_delete_fyle_import_tasks(
            workspace_general_settings_instance=workspace_general_settings,
            mapping_settings=MappingSetting.objects.filter(
                workspace_id=instance.workspace_id
            ).values()
        )


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
        chain = Chain()

        chain.append(
            'fyle_integrations_imports.tasks.trigger_import_via_schedule',
            instance.workspace_id,
            instance.destination_field,
            instance.source_field,
            'apps.xero.utils.XeroConnector',
            XeroCredentials.get_active_xero_credentials(workspace_id=instance.workspace_id),
            [SYNC_METHODS.get(instance.destination_field.upper(), 'tracking_categories')],
            is_auto_sync_allowed(WorkspaceGeneralSettings.objects.get(workspace_id=instance.workspace_id), instance),
            False,
            None,
            True
        )

        chain.run()


@receiver(post_save, sender=TenantMapping)
def run_post_tenant_mapping_trigger(sender, instance: TenantMapping, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_task("apps.xero.tasks.create_missing_currency", int(instance.workspace_id), q_options={'cluster': 'import'})
    async_task("apps.xero.tasks.update_xero_short_code", int(instance.workspace_id), q_options={'cluster': 'import'})
