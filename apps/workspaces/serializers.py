"""
Workspace Serializers
"""
from rest_framework import serializers

from .models import Workspace, FyleCredential, XeroCredentials, WorkspaceGeneralSettings, WorkspaceSchedule, LastExportDetail


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Workspace serializer
    """

    class Meta:
        model = Workspace
        fields = '__all__'


class FyleCredentialSerializer(serializers.ModelSerializer):
    """
    Fyle credential serializer
    """

    class Meta:
        model = FyleCredential
        fields = '__all__'


class XeroCredentialSerializer(serializers.ModelSerializer):
    """
    Xero credential serializer
    """

    class Meta:
        model = XeroCredentials
        fields = '__all__'


class WorkSpaceGeneralSettingsSerializer(serializers.ModelSerializer):
    """
    General settings serializer
    """
    class Meta:
        model = WorkspaceGeneralSettings
        fields = '__all__'


class WorkspaceScheduleSerializer(serializers.ModelSerializer):
    """
    Workspace Schedule Serializer
    """
    class Meta:
        model = WorkspaceSchedule
        fields = '__all__'

class LastExportDetailSerializer(serializers.ModelSerializer):
    """
    Last export detail serializer
    """
    class Meta:
        model = LastExportDetail
        fields = '__all__'
