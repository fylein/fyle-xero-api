from apps.xero.tasks import schedule_payment_creation, schedule_xero_objects_status_sync, schedule_reimbursements_sync
from apps.workspaces.models import WorkspaceGeneralSettings


class AdvancedSettingsTriggers:
    """
    Class containing all triggers for advanced_configurations
    """
    @staticmethod
    def run_workspace_general_settings_triggers(workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Run workspace general settings triggers
        """

        schedule_payment_creation(workspace_general_settings_instance.sync_fyle_to_xero_payments,\
            workspace_general_settings_instance.workspace.id)

        schedule_xero_objects_status_sync(
            sync_xero_to_fyle_payments=workspace_general_settings_instance.sync_xero_to_fyle_payments,
            workspace_id=workspace_general_settings_instance.workspace.id
        )

        schedule_reimbursements_sync(
            sync_xero_to_fyle_payments=workspace_general_settings_instance.sync_xero_to_fyle_payments,
            workspace_id=workspace_general_settings_instance.workspace.id
        )