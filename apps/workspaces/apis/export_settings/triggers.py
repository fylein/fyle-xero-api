from apps.mappings.tasks import schedule_auto_map_employees
from apps.workspaces.models import WorkspaceGeneralSettings

class ExportSettingsTrigger:
    """
    Class containing all triggers for Export Settings
    """
    @staticmethod
    def run_workspace_general_settings_triggers(workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Run workspace general settings triggers
        """
        schedule_auto_map_employees(workspace_general_settings_instance.auto_map_employees,
            workspace_general_settings_instance.workspace_id)
