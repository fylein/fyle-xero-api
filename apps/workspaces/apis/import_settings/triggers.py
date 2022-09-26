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
        schedule_tax_groups_creation(
            import_tax_codes=self.__workspace_general_settings.get('import_tax_codes'),
            workspace_id=self.__workspace_id
        )

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

        for setting in mapping_settings:
            if setting['source_field'] == 'PROJECT':
                projects_mapping_available = True
            elif setting['source_field'] == 'COST_CENTER':
                cost_center_mapping_available = True

        if not projects_mapping_available:
            schedule_projects_creation(False, self.__workspace_id)
        
        if not cost_center_mapping_available:
            schedule_cost_centers_creation(False, self.__workspace_id)
        
        schedule_fyle_attributes_creation(self.__workspace_id)

    def post_save_mapping_settings(self):
        """
        Post save actions for mapping settings
        """
        destination_fields = []
        for setting in self.__mapping_settings:
            destination_fields.append(setting['destination_field'])

        print(self.__mapping_settings)

        MappingSetting.objects.filter(
            ~Q(destination_field__in=destination_fields),
            destination_field__in=['CLASS', 'CUSTOMER', 'DEPARTMENT'],
            workspace_id=self.__workspace_id
        ).delete()
