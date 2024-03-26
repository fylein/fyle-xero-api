from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.queue import schedule_auto_map_employees
from apps.workspaces.models import WorkspaceGeneralSettings, LastExportDetail
from apps.workspaces.utils import delete_cards_mapping_settings, schedule_or_delete_import_supplier_schedule
from apps.fyle.models import ExpenseGroup
from apps.tasks.models import Error, TaskLog
from apps.xero.exceptions import update_last_export_details


class ExportSettingsTrigger:
    """
    Class containing all triggers for Export Settings
    """

    @staticmethod
    def run_workspace_general_settings_triggers(
        workspace_general_settings_instance: WorkspaceGeneralSettings,
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

        # Delete all the task_logs, errors for the not selected exports
        fund_source = []

        if workspace_general_settings_instance.reimbursable_expenses_object:
            fund_source.append('PERSONAL')
        if workspace_general_settings_instance.corporate_credit_card_expenses_object:
            fund_source.append('CCC')

        expense_group_ids = ExpenseGroup.objects.filter(
            workspace_id=workspace_id,
            exported_at__isnull=True
        ).exclude(fund_source__in=fund_source).values_list('id', flat=True)

        if expense_group_ids:
            Error.objects.filter(workspace_id = workspace_id, expense_group_id__in=expense_group_ids).delete()
            TaskLog.objects.filter(workspace_id = workspace_id, expense_group_id__in=expense_group_ids, status__in=['FAILED', 'FATAL']).delete()
            last_export_detail = LastExportDetail.objects.filter(workspace_id=workspace_id).first()
            if last_export_detail.last_exported_at:
                update_last_export_details(workspace_id)
