from rest_framework import serializers

from apps.workspaces.models import Workspace, WorkspaceGeneralSettings, WorkspaceSchedule
from apps.workspaces.tasks import schedule_sync
from apps.mappings.models import GeneralMapping
from .triggers import AdvancedSettingsTriggers


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


class WorkspaceScheduleSerializer(serializers.ModelSerializer):


    class Meta:
        model = WorkspaceSchedule
        fields = [
            'enabled',
            'interval_hours'
        ]


class WorkspaceGeneralSettingsSerializer(serializers.ModelSerializer):


    class Meta:
        model = WorkspaceGeneralSettings
        fields = [
            'change_accounting_period',
            'sync_fyle_to_xero_payments',
            'sync_xero_to_fyle_payments',
            'auto_create_destination_entity'
        ]


class GeneralMappingsSerializer(serializers.ModelSerializer):
    payment_account = ReadWriteSerializerMethodField()


    class Meta:
        model = GeneralMapping
        fields = [
            'payment_account'
        ]

    def get_payment_account(self, instance):
        return {
            'name': instance.payment_account_name,
            'id': instance.payment_account_id
        }


class AdvancedSettingsSerializer(serializers.ModelSerializer):
    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    workspace_schedules = WorkspaceScheduleSerializer()
    workspace_id = serializers.SerializerMethodField()


    class Meta:
        model = Workspace
        fields = [
            'workspace_general_settings',
            'general_mappings',
            'workspace_schedules',
            'workspace_id'
        ]
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id
    
    def update(self, instance, validated):
        workspace_general_settings = validated.pop('workspace_general_settings')
        general_mappings = validated.pop('general_mappings')
        workspace_schedules = validated.pop('workspace_schedules')

        workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace=instance,
            defaults={
                'change_accounting_period' : workspace_general_settings.get('change_accounting_period'),
                'sync_fyle_to_xero_payments': workspace_general_settings.get('sync_fyle_to_xero_payments'),
                'sync_xero_to_fyle_payments' : workspace_general_settings.get('sync_xero_to_fyle_payments'),
                'auto_create_destination_entity' : workspace_general_settings.get('auto_create_destination_entity')
            }
        )

        GeneralMapping.objects.update_or_create(
            workspace = instance,
            defaults={
                'payment_account_name' : general_mappings.get('payment_account').get('name'),
                'payment_account_id' : general_mappings.get('payment_account').get('id')
            }
        )

        schedule_sync(
            workspace_id=instance.id,
            schedule_enabled=workspace_schedules.get('enabled'),
            hours=workspace_schedules.get('interval_hours'),
        )

        AdvancedSettingsTriggers.run_workspace_general_settings_triggers(workspace_general_settings_instance)

        if instance.onboarding_state == 'ADVANCED_SETTINGS':
            instance.onboarding_state = 'COMPLETE'
            instance.save()

        return instance

    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')

        if not data.get('workspace_schedules'):
            raise serializers.ValidationError('Workspace Schedules are required')

        return data