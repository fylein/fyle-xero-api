from typing import Dict, List
from django.db.models import Q

from apps.mappings.tasks import schedule_categories_creation, schedule_cost_centers_creation, schedule_tax_groups_creation, schedule_projects_creation, schedule_fyle_attributes_creation
from fyle_accounting_mappings.models import MappingSetting


class ImportSettingsTrigger:
    """
    All the post save actions of Import Settings API
    """
    def __init__(self, workspace_general_settings: Dict, mapping_settings: List[Dict], workspace_id):
        self.__workspace_general_settings = workspace_general_settings
        self.__mapping_settings = mapping_settings
        self.__workspace_id = workspace_id

    def post_save_workspace_general_settings(self):
        """
        Post save action for workspace general settings
        """
        #This will take care of auto creating tax mappings
        schedule_tax_groups_creation(
            import_tax_codes=self.__workspace_general_settings.get('import_tax_codes'),
            workspace_id=self.__workspace_id
        )

        #This will take care of auto creating category mappings
        schedule_categories_creation(
            import_categories=self.__workspace_general_settings.get('import_categories'),
            workspace_id=self.__workspace_id
        )
    
    def pre_save_mapping_settings(self):
        """
        Post save action for mapping settings
        """
        mapping_settings = self.__mapping_settings

        projects_mapping_available = False
        cost_center_mapping_available = False

        #Here we are checking if any of the mappings have PROJECT and COST_CENTER mapping
        for setting in mapping_settings:
            if setting['source_field'] == 'PROJECT':
                projects_mapping_available = True
            elif setting['source_field'] == 'COST_CENTER':
                cost_center_mapping_available = True

        #Based on the value if PROJECT and COST_CENTER mapping is not present we are clearing out the schedules from the DB.
        if not projects_mapping_available:
            schedule_projects_creation(False, self.__workspace_id)
        
        if not cost_center_mapping_available:
            schedule_cost_centers_creation(False, self.__workspace_id)
        
        #Schdule for auto craeting custom field mappings
        schedule_fyle_attributes_creation(self.__workspace_id)

    def post_save_mapping_settings(self):
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
