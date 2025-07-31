import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping

from apps.fyle.enums import FyleAttributeEnum
from apps.mappings.models import TenantMapping
from apps.workspaces.helpers import patch_integration_settings_for_unmapped_cards
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def post_delete_xero_connection(workspace_id):
    """
    Post delete xero connection
    :return: None
    """
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.onboarding_state in ("CONNECTION", "EXPORT_SETTINGS"):
        TenantMapping.objects.filter(workspace_id=workspace_id).delete()
        Mapping.objects.filter(
            workspace_id=workspace_id, source_type=FyleAttributeEnum.EMPLOYEE
        ).delete()
        DestinationAttribute.objects.filter(workspace_id=workspace_id).delete()
        workspace.onboarding_state = "CONNECTION"
        workspace.xero_short_code = None
        workspace.xero_currency = None
        workspace.save()


@receiver(post_save, sender=WorkspaceGeneralSettings)
def run_post_workspace_general_settings_triggers(sender: type[WorkspaceGeneralSettings], instance: WorkspaceGeneralSettings, **kwargs) -> None:
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    logger.info('Running post configuration triggers for workspace_id: %s', instance.workspace_id)

    if instance.corporate_credit_card_expenses_object:
        unmapped_card_count = ExpenseAttribute.objects.filter(
            attribute_type="CORPORATE_CARD", workspace_id=instance.workspace_id, active=True, mapping__isnull=True
        ).count()
        patch_integration_settings_for_unmapped_cards(workspace_id=instance.workspace_id, unmapped_card_count=unmapped_card_count)
    elif instance.corporate_credit_card_expenses_object is None:
        patch_integration_settings_for_unmapped_cards(workspace_id=instance.workspace_id, unmapped_card_count=0)
