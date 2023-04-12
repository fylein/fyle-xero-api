from apps.workspaces.models import Workspace
from rest_framework import serializers

from django.db import transaction

from apps.workspaces.apis.export_settings.serializers import ExportSettingsSerializer, \
    ReadWriteSerializerMethodField

from apps.workspaces.apis.import_settings.serializers import ImportSettingsSerializer
from apps.workspaces.apis.advanced_settings.serializers import AdvancedSettingsSerializer


class CloneSettingsSerializer(serializers.ModelSerializer):
    export_settings = ReadWriteSerializerMethodField()
    import_settings = ReadWriteSerializerMethodField()
    advanced_settings = ReadWriteSerializerMethodField()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'workspace_id',
            'export_settings',
            'import_settings',
            'advanced_settings'
        ]
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id
    
    def get_export_settings(self, instance):
        return ExportSettingsSerializer(instance).data

    def get_import_settings(self, instance):
        return ImportSettingsSerializer(instance).data
    
    def get_advanced_settings(self, instance):
        return AdvancedSettingsSerializer(instance).data
    
    def update(self, instance, validated):
        export_settings = validated.pop('export_settings')
        import_settings = validated.pop('import_settings')
        advanced_settings = validated.pop('advanced_settings')

        export_settings_serializer = ExportSettingsSerializer(
            instance, data=export_settings, partial=True
        )

        import_settings_serializer = ImportSettingsSerializer(
            instance, data=import_settings, partial=True
        )

        advanced_settings_serializer = AdvancedSettingsSerializer(
            instance, data=advanced_settings, partial=True
        )

        if export_settings_serializer.is_valid(raise_exception=True) and \
            import_settings_serializer.is_valid(raise_exception=True) and \
                advanced_settings_serializer.is_valid(raise_exception=True):

            # Doing all these in a transaction block to make sure we revert 
            # to old state when one of the serializer fails
            with transaction.atomic():
                export_settings_serializer.save()
                import_settings_serializer.save()
                advanced_settings_serializer.save()

        return instance
    
    def validate(self, data):
        if not data.get('export_settings'):
            raise serializers.ValidationError('Export Settings are required')

        if not data.get('import_settings'):
            raise serializers.ValidationError('Import Settings are required')
        
        if not data.get('advanced_settings'):
            raise serializers.ValidationError('Advanced Settings are required')

        return data
