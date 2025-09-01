from apps.workspaces.apis.export_settings.helpers import clear_workspace_errors_on_export_type_change
from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.queue import schedule_auto_map_employees
from apps.workspaces.models import WorkspaceGeneralSettings, LastExportDetail
from apps.workspaces.utils import delete_cards_mapping_settings, schedule_or_delete_import_supplier_schedule
from apps.xero.exceptions import update_last_export_details


class ExportSettingsTrigger:
    """
    Class containing all triggers for Export Settings
    """

    @staticmethod
    def run_workspace_general_settings_triggers(
        workspace_general_settings_instance: WorkspaceGeneralSettings,
        old_configurations: dict,
    ):
        """
        Run workspace general settings triggers
        """
        workspace_id = workspace_general_settings_instance.workspace_id

        MappingSetting.objects.update_or_create(
            destination_field="CONTACT",
            workspace_id=workspace_general_settings_instance.workspace_id,
            source_field="EMPLOYEE",
            defaults={
                "import_to_fyle": False,
                "is_custom": False,
                "source_placeholder": None,
            },
        )

        delete_cards_mapping_settings(workspace_general_settings_instance)

        schedule_or_delete_import_supplier_schedule(workspace_general_settings_instance)

        schedule_auto_map_employees(
            workspace_general_settings_instance.auto_map_employees,
            workspace_general_settings_instance.workspace_id,
        )

        if workspace_general_settings_instance and old_configurations:
            clear_workspace_errors_on_export_type_change(workspace_id, old_configurations, workspace_general_settings_instance)

            last_export_detail = LastExportDetail.objects.filter(workspace_id=workspace_id).first()
            if last_export_detail.last_exported_at:
                update_last_export_details(workspace_id)
