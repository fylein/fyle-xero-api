from apps.mappings.tasks import schedule_auto_map_employees
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_accounting_mappings.models import MappingSetting
from apps.workspaces.utils import delete_cards_mapping_settings


class ExportSettingsTrigger:
    """
    Class containing all triggers for Export Settings
    """
    @staticmethod
    def run_workspace_general_settings_triggers(workspace_general_settings_instance: WorkspaceGeneralSettings, import_card_credits):
        """
        Run workspace general settings triggers
        """
        MappingSetting.objects.update_or_create(
            destination_field='CONTACT',
            workspace_id=workspace_general_settings_instance.workspace_id,
            source_field='EMPLOYEE',
            defaults={
                'import_to_fyle': False,
                'is_custom': False,
                'source_placeholder': None
            }
        )

        delete_cards_mapping_settings(workspace_general_settings_instance,import_card_credits)

        schedule_auto_map_employees(workspace_general_settings_instance.auto_map_employees,
            workspace_general_settings_instance.workspace_id)
