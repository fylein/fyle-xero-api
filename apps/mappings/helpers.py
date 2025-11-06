import logging

from fyle_accounting_mappings.models import ExpenseAttribute, MappingSetting

from apps.workspaces.helpers import patch_integration_settings_for_unmapped_cards
from apps.workspaces.models import WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def is_auto_sync_allowed(workspace_general_settings: WorkspaceGeneralSettings, mapping_setting: MappingSetting = None):
    """
    Get the auto sync permission
    :return: bool
    """
    is_auto_sync_status_allowed = False
    if (mapping_setting and mapping_setting.destination_field == 'CUSTOMER' and mapping_setting.source_field == 'PROJECT') or workspace_general_settings.import_categories:
        is_auto_sync_status_allowed = True

    return is_auto_sync_status_allowed


def prepend_code_to_name(prepend_code_in_name: bool, value: str, code: str = None) -> str:
    """
    Format the attribute name based on the use_code_in_naming flag
    """
    if prepend_code_in_name and code:
        return "{}: {}".format(code, value)
    return value


def patch_corporate_card_integration_settings(workspace_id: int) -> None:
    """
    Patch integration settings for unmapped corporate cards.
    This is called when corporate card mapping is created or when a corporate card is created via webhook.

    :param workspace_id: Workspace ID
    :return: None
    """
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

    if workspace_general_settings and workspace_general_settings.corporate_credit_card_expenses_object == 'BANK TRANSACTION':
        unmapped_card_count = ExpenseAttribute.objects.filter(
            attribute_type="CORPORATE_CARD", workspace_id=workspace_id, active=True, mapping__isnull=True
        ).count()

        patch_integration_settings_for_unmapped_cards(workspace_id=workspace_id, unmapped_card_count=unmapped_card_count)
        logger.info(f"Patched integration settings for workspace {workspace_id}, unmapped card count: {unmapped_card_count}")
