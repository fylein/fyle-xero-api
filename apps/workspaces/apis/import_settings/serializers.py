from rest_framework import serializers
from fyle_accounting_mappings.models import MappingSetting
from django.db import transaction
from django.db.models import Q

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.mappings.models import GeneralMapping
from .triggers import ImportSettingsTrigger



class MappingSettingFilteredListSerializer(serializers.ListSerializer):
    """
    Serializer to filter the active system, which is a boolen field in
    System Model. The value argument to to_representation() method is
    the model instance
    """

    def to_representation(self, data):
        data = data.filter(~Q(destination_field__in=['TAX_CODE', 'ACCOUNT', 'BANK_ACCOUNT', 'CUSTOMER', 'CONTACT']))
        return super(MappingSettingFilteredListSerializer, self).to_representation(data)


class ReadWriteSerializerMethodField(serializers.SerializerMethodField):
    """
    Serializer Method Field to Read and Write from values
    Inherits serializers.SerializerMethodField
    """

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return {
            self.field_name: data
        }


class MappingSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MappingSetting
        list_serializer_class = MappingSettingFilteredListSerializer
        fields = [
            'source_field',
            'destination_field',
            'import_to_fyle',
            'is_custom',
            'source_placeholder'
        ]


class WorkspaceGeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceGeneralSettings
        fields = ['import_categories', 'charts_of_accounts', 'import_tax_codes', 'import_customers']


class GeneralMappingsSerializer(serializers.ModelSerializer):
    default_tax_code = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = [
            'default_tax_code'
        ]

    def get_default_tax_code(self, instance):
        return {
            'name': instance.default_tax_code_name,
            'id': instance.default_tax_code_id
        }


class ImportSettingsSerializer(serializers.ModelSerializer):
    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    mapping_settings = MappingSettingSerializer(many=True)
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'workspace_general_settings',
            'general_mappings',
            'mapping_settings',
            'workspace_id'
        ]
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id
    
    def update(self, instance, validated):
        workspace_general_settings = validated.pop('workspace_general_settings')
        general_mappings = validated.pop('general_mappings')
        mapping_settings = validated.pop('mapping_settings')

        with transaction.atomic():
            WorkspaceGeneralSettings.objects.update_or_create(
                workspace=instance,
                defaults={
                    'import_categories': workspace_general_settings.get('import_categories'),
                    'charts_of_accounts': workspace_general_settings.get('charts_of_accounts'),
                    'import_tax_codes': workspace_general_settings.get('import_tax_codes'),
                    'import_customers': workspace_general_settings.get('import_customers')
                }
            )

<<<<<<< HEAD
        GeneralMapping.objects.update_or_create(
            workspace=instance,
            defaults={
                'default_tax_code_name': general_mappings.get('default_tax_code').get('name'),
                'default_tax_code_id': general_mappings.get('default_tax_code').get('id')
            }
        )
        
        trigger: ImportSettingsTrigger = ImportSettingsTrigger(
            workspace_general_settings=workspace_general_settings,
            mapping_settings=mapping_settings,
            workspace_id=instance.id
        )

        trigger.post_save_workspace_general_settings()
        trigger.pre_save_mapping_settings()

        if workspace_general_settings['import_tax_codes']:
=======
            GeneralMapping.objects.update_or_create(
                workspace=instance,
                defaults={
                    'default_tax_code_name': general_mappings.get('default_tax_code').get('name'),
                    'default_tax_code_id': general_mappings.get('default_tax_code').get('id')
                }
            )
            
            if workspace_general_settings['import_tax_codes']:
                mapping_settings.append({
                    'source_field': 'TAX_GROUP',
                    'destination_field': 'TAX_CODE',
                    'import_to_fyle': True,
                    'is_custom': False
                })

            if workspace_general_settings['import_customers']:
                mapping_settings.append({
                    'source_field': 'PROJECT',
                    'destination_field': 'CUSTOMER',
                    'import_to_fyle': True,
                    'is_custom': False
                })
            
>>>>>>> onboarding-api-1-placeholder
            mapping_settings.append({
                'source_field': 'CATEGORY',
                'destination_field': 'ACCOUNT',
                'import_to_fyle': True,
                'is_custom': False
            })

        
            for setting in mapping_settings:
                MappingSetting.objects.update_or_create(
                    destination_field=setting['destination_field'],
                    workspace_id=instance.id,
                    defaults={
                        'source_field': setting['source_field'],
                        'import_to_fyle': setting['import_to_fyle'] if 'import_to_fyle' in setting else False,
                        'is_custom': setting['is_custom'] if 'is_custom' in setting else False,
                        'source_placeholder': setting['source_placeholder'] if 'source_placeholder' in setting else None
                    }
                )
        
        trigger.post_save_mapping_settings()

        if instance.onboarding_state == 'IMPORT_SETTINGS':
            instance.onboarding_state = 'ADVANCED_CONFIGURATION'
            instance.save()

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if data.get('mapping_settings') is None:
            raise serializers.ValidationError('Mapping settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')
        return data
