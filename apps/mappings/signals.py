"""
Mappings Signal
"""

import logging
from datetime import datetime, timedelta, timezone

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from fyle.platform.exceptions import WrongParamsError
from fyle_accounting_mappings.models import Mapping, MappingSetting
from fyle_integrations_platform_connector import PlatformConnector
from rest_framework.exceptions import ValidationError

from apps.fyle.enums import FyleAttributeEnum
from apps.mappings.constants import SYNC_METHODS
from apps.mappings.helpers import patch_corporate_card_integration_settings
from apps.mappings.models import TenantMapping
from apps.mappings.schedules import new_schedule_or_delete_fyle_import_tasks
from apps.tasks.models import Error
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.utils import XeroConnector
from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.modules.expense_custom_fields import ExpenseCustomField
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq

logger = logging.getLogger(__name__)
logger.level = logging.INFO


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


@receiver(post_save, sender=Mapping)
def patch_integration_settings_on_card_mapping(sender, instance: Mapping, created: bool, **kwargs):
    """
    Patch integration settings when corporate card mapping is created
    """
    if instance.source_type == 'CORPORATE_CARD' and created:
        patch_corporate_card_integration_settings(workspace_id=instance.workspace_id)


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
        try:
            workspace_id = int(instance.workspace_id)
            # Checking is import_log exists or not if not create one
            import_log, is_created = ImportLog.objects.get_or_create(
                workspace_id=workspace_id,
                attribute_type=instance.source_field,
                defaults={
                    'status': 'IN_PROGRESS'
                }
            )

            last_successful_run_at = None
            if import_log and not is_created:
                last_successful_run_at = import_log.last_successful_run_at or None
                time_difference = datetime.now() - timedelta(minutes=30)
                offset_aware_time_difference = time_difference.replace(tzinfo=timezone.utc)

                if (
                    last_successful_run_at and offset_aware_time_difference
                    and (offset_aware_time_difference < last_successful_run_at)
                ):
                    import_log.last_successful_run_at = offset_aware_time_difference
                    last_successful_run_at = offset_aware_time_difference
                    import_log.save()

            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
            xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

            # Creating the expense_custom_field object with the correct last_successful_run_at value
            expense_custom_field = ExpenseCustomField(
                workspace_id=workspace_id,
                source_field=instance.source_field,
                destination_field=instance.destination_field,
                sync_after=last_successful_run_at,
                sdk_connection=xero_connection,
                destination_sync_methods=[SYNC_METHODS.get(instance.destination_field.upper(), 'tracking_categories')]
            )

            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials=fyle_credentials)

            import_log.status = 'IN_PROGRESS'
            import_log.save()

            expense_custom_field.sync_expense_attributes(platform=platform)
            expense_custom_field.construct_payload_and_import_to_fyle(platform=platform, import_log=import_log)
            expense_custom_field.sync_expense_attributes(platform=platform)

        except WrongParamsError as error:
            logger.error(
                'Error while creating %s workspace_id - %s in Fyle %s %s',
                instance.source_field, instance.workspace_id, error.message, {'error': error.response}
            )
            if error.response and 'message' in error.response:
                raise ValidationError({
                    'message': error.response['message'],
                    'field_name': instance.source_field
                })

        # setting the import_log.last_successful_run_at to -30mins for the post_save_trigger
        import_log = ImportLog.objects.filter(workspace_id=workspace_id, attribute_type=instance.source_field).first()
        if import_log.last_successful_run_at:
            last_successful_run_at = import_log.last_successful_run_at - timedelta(minutes=30)
            import_log.last_successful_run_at = last_successful_run_at
            import_log.save()


@receiver(post_save, sender=TenantMapping)
def run_post_tenant_mapping_trigger(sender, instance: TenantMapping, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    payload = {
        'workspace_id': int(instance.workspace_id),
        'action': WorkerActionEnum.CREATE_MISSING_CURRENCY.value,
        'data': {
            'workspace_id': int(instance.workspace_id)
        }
    }
    publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.IMPORT.value)

    payload = {
        'workspace_id': int(instance.workspace_id),
        'action': WorkerActionEnum.UPDATE_XERO_SHORT_CODE.value,
        'data': {
            'workspace_id': int(instance.workspace_id)
        }
    }
    publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.IMPORT.value)
