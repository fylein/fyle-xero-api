"""
Workspace Serializers
"""
from rest_framework import serializers

from apps.workspaces.models import (
    FyleCredential,
    LastExportDetail,
    Workspace,
    WorkspaceGeneralSettings,
    WorkspaceSchedule,
    XeroCredentials,
)


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Workspace serializer
    """

    class Meta:
        model = Workspace
        fields = "__all__"


class FyleCredentialSerializer(serializers.ModelSerializer):
    """
    Fyle credential serializer
    """

    class Meta:
        model = FyleCredential
        fields = "__all__"


class XeroCredentialSerializer(serializers.ModelSerializer):
    """
    Xero credential serializer
    """

    class Meta:
        model = XeroCredentials
        fields = "__all__"


class WorkSpaceGeneralSettingsSerializer(serializers.ModelSerializer):
    """
    General settings serializer
    """

    class Meta:
        model = WorkspaceGeneralSettings
        exclude = ['skip_accounting_export_summary_post']


class WorkspaceScheduleSerializer(serializers.ModelSerializer):
    """
    Workspace Schedule Serializer
    """

    class Meta:
        model = WorkspaceSchedule
        fields = "__all__"


class LastExportDetailSerializer(serializers.ModelSerializer):
    """
    Last export detail serializer
    """

    class Meta:
        model = LastExportDetail
        exclude = ['unmapped_card_count']
