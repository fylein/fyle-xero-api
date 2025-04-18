from datetime import datetime, timezone
from typing import Dict, List

from django.db.models import Q
from fyle_accounting_mappings.models import ExpenseAttribute, MappingSetting

from apps.mappings.schedules import new_schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_integrations_imports.models import ImportLog


class ImportSettingsTrigger:
    """
    All the post save actions of Import Settings API
    """

    def __init__(
        self,
        workspace_general_settings: Dict,
        mapping_settings: List[Dict],
        workspace_id,
    ):
        self.__workspace_general_settings = workspace_general_settings
        self.__mapping_settings = mapping_settings
        self.__workspace_id = workspace_id

    def pre_save_workspace_general_settings(self, workspace_general_settings):
        """
        Pre save action for workspace general settings
        """
        current_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=self.__workspace_id).first()

        if current_general_settings and current_general_settings.charts_of_accounts and current_general_settings.charts_of_accounts != workspace_general_settings.get("charts_of_accounts"):
            import_log = ImportLog.objects.filter(workspace_id=self.__workspace_id, attribute_type='CATEGORY').first()
            if import_log:
                import_log.last_successful_run_at = None
                import_log.save()

    def post_save_workspace_general_settings(
        self, workspace_general_settings_instance: WorkspaceGeneralSettings
    ):
        """
        Post save action for workspace general settings
        """
        if not self.__workspace_general_settings.get("import_customers"):
            MappingSetting.objects.filter(
                workspace_id=self.__workspace_id,
                source_field="PROJECT",
                destination_field="CUSTOMER",
            ).delete()

        new_schedule_or_delete_fyle_import_tasks(
            workspace_general_settings_instance=workspace_general_settings_instance,
            mapping_settings=self.__mapping_settings,
        )

    def __unset_auto_mapped_flag(self, current_mapping_settings: List[MappingSetting], new_mappings_settings: List[Dict]):
        """
        Set the auto_mapped flag to false for the expense_attributes for the attributes
        whose mapping is changed.
        """
        changed_source_fields = []

        for new_setting in new_mappings_settings:
            destination_field = new_setting['destination_field']
            source_field = new_setting['source_field']
            current_setting = current_mapping_settings.filter(destination_field=destination_field).first()
            if current_setting and current_setting.source_field != source_field:
                changed_source_fields.append(current_setting.source_field)

        ExpenseAttribute.objects.filter(workspace_id=self.__workspace_id, attribute_type__in=changed_source_fields).update(auto_mapped=False, updated_at=datetime.now(timezone.utc))

    def __reset_import_log_timestamp(
            self,
            current_mapping_settings: List[MappingSetting],
            new_mappings_settings: List[Dict],
            workspace_id: int
    ) -> None:
        """
        Reset Import logs when mapping settings are deleted or the source_field is changed.
        """
        changed_source_fields = set()

        for new_setting in new_mappings_settings:
            destination_field = new_setting['destination_field']
            source_field = new_setting['source_field']
            current_setting = current_mapping_settings.filter(source_field=source_field).first()
            if current_setting and current_setting.destination_field != destination_field:
                changed_source_fields.add(current_setting.source_field)

        current_source_fields = set(mapping_setting.source_field for mapping_setting in current_mapping_settings)
        new_source_fields = set(mapping_setting['source_field'] for mapping_setting in new_mappings_settings)
        deleted_source_fields = current_source_fields.difference(new_source_fields | {'CORPORATE_CARD', 'CATEGORY'})

        reset_source_fields = changed_source_fields.union(deleted_source_fields)

        ImportLog.objects.filter(workspace_id=workspace_id, attribute_type__in=reset_source_fields).update(last_successful_run_at=None, updated_at=datetime.now(timezone.utc))

    def pre_save_mapping_settings(self, pre_save_workspace_general_settings: WorkspaceGeneralSettings = None):
        """
        Post save action for mapping settings
        """
        mapping_settings = self.__mapping_settings

        current_mapping_settings = MappingSetting.objects.filter(workspace_id=self.__workspace_id).all()
        self.__unset_auto_mapped_flag(current_mapping_settings, mapping_settings)
        self.__reset_import_log_timestamp(
            current_mapping_settings=current_mapping_settings,
            new_mappings_settings=mapping_settings,
            workspace_id=self.__workspace_id
        )

        if pre_save_workspace_general_settings:
            workspace_settings = self.__workspace_general_settings
            old_coa = set(pre_save_workspace_general_settings.charts_of_accounts or [])
            new_coa = set(workspace_settings['charts_of_accounts'] or [])

            if workspace_settings['import_categories'] and old_coa != new_coa:
                ImportLog.objects.filter(workspace_id=self.__workspace_id, attribute_type='CATEGORY').update(last_successful_run_at=None, updated_at=datetime.now(timezone.utc))

    def post_save_mapping_settings(
        self, workspace_general_settings_instance: WorkspaceGeneralSettings
    ):
        """
        Post save actions for mapping settings
        Here we need to clear out the data from the mapping-settings table for consecutive runs.
        """
        # We first need to avoid deleting mapping-settings that are always necessary.
        destination_fields = [
            "TAX_CODE",
            "ACCOUNT",
            "BANK_ACCOUNT",
            "CUSTOMER",
            "CONTACT",
        ]

        # Here we are filtering out the mapping_settings payload and adding the destination-fields that are present in the payload
        # So that we avoid deleting them.
        for setting in self.__mapping_settings:
            if setting["destination_field"] not in destination_fields:
                destination_fields.append(setting["destination_field"])

        # Now that we have all the system necessary mapping-settings and the mapping-settings in the payload
        # This query will take care of deleting all the redundant mapping-settings that are not required.
        MappingSetting.objects.filter(
            ~Q(destination_field__in=destination_fields),
            workspace_id=self.__workspace_id,
        ).delete()

        new_schedule_or_delete_fyle_import_tasks(
            workspace_general_settings_instance=workspace_general_settings_instance,
            mapping_settings=self.__mapping_settings,
        )
