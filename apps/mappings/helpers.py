from fyle_accounting_mappings.models import MappingSetting
from apps.workspaces.models import WorkspaceGeneralSettings


def is_auto_sync_allowed(workspace_general_settings: WorkspaceGeneralSettings, mapping_setting: MappingSetting = None):
    """
    Get the auto sync permission
    :return: bool
    """
    is_auto_sync_status_allowed = False
    if (mapping_setting and mapping_setting.destination_field == 'CUSTOMER' and mapping_setting.source_field == 'PROJECT') or workspace_general_settings.import_categories:
        is_auto_sync_status_allowed = True

    return is_auto_sync_status_allowed
