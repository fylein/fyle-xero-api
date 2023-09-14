from typing import Dict, List
from django.db.models import Q

from apps.mappings.queue import schedule_cost_centers_creation, schedule_tax_groups_creation,\
    schedule_fyle_attributes_creation
from apps.mappings.helpers import schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_accounting_mappings.models import MappingSetting


class ImportSettingsTrigger:
    """
    All the post save actions of Import Settings API
    """
    def __init__(self, workspace_general_settings: Dict, mapping_settings: List[Dict], workspace_id):
        self.__workspace_general_settings = workspace_general_settings
        self.__mapping_settings = mapping_settings
        self.__workspace_id = workspace_id

    def post_save_workspace_general_settings(self, workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Post save action for workspace general settings
        """
        #This will take care of auto creating tax mappings
        schedule_tax_groups_creation(
            import_tax_codes=self.__workspace_general_settings.get('import_tax_codes'),
            workspace_id=self.__workspace_id
        )

        if not self.__workspace_general_settings.get('import_customers'):
            MappingSetting.objects.filter(
                workspace_id=self.__workspace_id, 
                source_field='PROJECT',
                destination_field='CUSTOMER'
            ).delete()

        schedule_or_delete_fyle_import_tasks(workspace_general_settings_instance)

    def pre_save_mapping_settings(self):
        """
        Post save action for mapping settings
        """
        mapping_settings = self.__mapping_settings

        cost_center_mapping_available = False

        #Here we are checking if any of the mappings have PROJECT and COST_CENTER mapping
        for setting in mapping_settings:
            if setting['source_field'] == 'COST_CENTER':
                cost_center_mapping_available = True
        
        if not cost_center_mapping_available:
            schedule_cost_centers_creation(False, self.__workspace_id)
        
        #Schdule for auto creating custom field mappings
        schedule_fyle_attributes_creation(self.__workspace_id)

    def post_save_mapping_settings(self, workspace_general_settings_instance: WorkspaceGeneralSettings):
        """
        Post save actions for mapping settings
        Here we need to clear out the data from the mapping-settings table for consecutive runs.
        """
        #We first need to avoid deleting mapping-settings that are always necessary.
        destination_fields = ['TAX_CODE', 'ACCOUNT', 'BANK_ACCOUNT', 'CUSTOMER', 'CONTACT']
        
        #Here we are filtering out the mapping_settings payload and adding the destination-fields that are present in the payload
        #So that we avoid deleting them.
        for setting in self.__mapping_settings:
            if setting['destination_field'] not in destination_fields:
                destination_fields.append(setting['destination_field'])
        
        #Now that we have all the system necessary mapping-settings and the mapping-settings in the payload
        #This query will take care of deleting all the redundant mapping-settings that are not required.
        MappingSetting.objects.filter(
            ~Q(destination_field__in=destination_fields),
            workspace_id=self.__workspace_id
        ).delete()

        schedule_or_delete_fyle_import_tasks(workspace_general_settings_instance)
