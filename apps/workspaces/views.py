import logging

from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from fyle_rest_auth.utils import AuthUtils

from fyle_xero_api.utils import assert_valid

from .models import Workspace, XeroCredentials, WorkspaceGeneralSettings, LastExportDetail
from .utils import generate_xero_identity, create_or_update_general_settings
from .serializers import WorkspaceSerializer, XeroCredentialSerializer, \
    WorkSpaceGeneralSettingsSerializer, LastExportDetailSerializer
from .tasks import export_to_xero
from apps.exceptions import handle_view_exceptions
from .actions import connect_xero, post_workspace, revoke_connections, get_workspace_admin

logger = logging.getLogger(__name__)


User = get_user_model()
auth_utils = AuthUtils()


class ReadyView(viewsets.ViewSet):
    """
    Ready call
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Ready call
        """

        Workspace.objects.raw('Select 1 from workspaces_workspace')

        return Response(
            data={
                'message': 'Ready'
            },
            status=status.HTTP_200_OK
        )


class WorkspaceView(viewsets.ViewSet):
    """
    Xero Workspace
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a Workspace
        """
        access_token = request.META.get('HTTP_AUTHORIZATION')
        workspace = post_workspace(access_token=access_token,request=request)

        return Response(
            data=WorkspaceSerializer(workspace).data,
            status=status.HTTP_200_OK
        )

    def get(self, request):
        """
        Get workspace
        """
        user = User.objects.get(user_id=request.user)
        org_id = request.query_params.get('org_id')
        workspace = Workspace.objects.filter(user__in=[user], fyle_org_id=org_id).all()

        return Response(
            data=WorkspaceSerializer(workspace, many=True).data,
            status=status.HTTP_200_OK
        )

    @handle_view_exceptions()
    def get_by_id(self, request, **kwargs):
        """
        Get Workspace by id
        """

        user = User.objects.get(user_id=request.user)
        workspace = Workspace.objects.get(pk=kwargs['workspace_id'], user=user)

        return Response(
            data=WorkspaceSerializer(workspace).data if workspace else {},
            status=status.HTTP_200_OK
        )


    def patch(self, request, **kwargs):
        """
        PATCH workspace
        """
        workspace_instance = Workspace.objects.get(pk=kwargs['workspace_id'])
        serializer = WorkspaceSerializer(
            workspace_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )


class ConnectXeroView(viewsets.ViewSet):
    """
    Xero Connect Oauth View
    """
    @handle_view_exceptions()
    def post(self, request, **kwargs):
        """
        Post of Xero Credentials
        """
    
        authorization_code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')

        xero_credentials = connect_xero(authorization_code=authorization_code, redirect_uri=redirect_uri, workspace_id=kwargs['workspace_id']) 

        return Response(
            data=XeroCredentialSerializer(xero_credentials).data,
            status=status.HTTP_200_OK
        )
        
    @handle_view_exceptions()
    def get(self, request, **kwargs):
        """
        Get Xero Credentials in Workspace
        """
    
        xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'], is_expired=False, refresh_token__isnull=False)

        return Response(
            data=XeroCredentialSerializer(xero_credentials).data,
            status=status.HTTP_200_OK
        )


class RevokeXeroConnectionView(viewsets.ViewSet):
    """
    Xero Revoke Xero Connection View
    """
    def post(self, request, **kwargs):
        """
        Post of Xero Credentials
        """
        # TODO: cleanup later - merge with ConnectXeroView
        revoke_connections(workspace_id=kwargs['workspace_id'])

        return Response(
            data={
                'message': 'Revoked Xero connection'
            },
            status=status.HTTP_200_OK
        )


class GeneralSettingsView(viewsets.ViewSet):
    """
    General Settings
    """
    serializer_class = WorkSpaceGeneralSettingsSerializer
    queryset = WorkspaceGeneralSettings.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Post workspace general settings
        """
        general_settings_payload = request.data

        assert_valid(general_settings_payload is not None, 'Request body is empty')

        workspace_id = kwargs['workspace_id']

        general_settings = create_or_update_general_settings(general_settings_payload, workspace_id)
        return Response(
            data=self.serializer_class(general_settings).data,
            status=status.HTTP_200_OK
        )

    @handle_view_exceptions()
    def get(self, request, *args, **kwargs):
        """
        Get workspace general settings
        """

        general_settings = self.queryset.get(workspace_id=kwargs['workspace_id'])
        return Response(
            data=self.serializer_class(general_settings).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, **kwargs):
        """
        PATCH workspace general settings
        """
        workspace_general_settings_object = WorkspaceGeneralSettings.objects.get(workspace_id=kwargs['workspace_id'])
        serializer = WorkSpaceGeneralSettingsSerializer(
            workspace_general_settings_object, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

class XeroExternalSignUpsView(viewsets.ViewSet):
    """
    Xero External Sign Ups
    """
    authentication_classes = []
    permission_classes = []

    @handle_view_exceptions()
    def post(self, request, **kwargs):
        """
        Post Xero External Sign Ups
        """

        authorization_code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        identity = generate_xero_identity(authorization_code, redirect_uri)

        return Response(
            data=identity,
            status=status.HTTP_200_OK
        )


class ExportToXeroView(viewsets.ViewSet):
    """
    Export Expenses to QBO
    """

    def post(self, request, *args, **kwargs):
        export_to_xero(workspace_id=kwargs['workspace_id'])

        return Response(
            status=status.HTTP_200_OK
        )


class LastExportDetailView(viewsets.ViewSet):
    """
    Last Export Details
    """
    serializer_class = LastExportDetailSerializer

    def get(self, request, *args, **kwargs):
        """
        last export detail
        """
        last_export_detail = LastExportDetail.objects.filter(workspace_id=kwargs['workspace_id']).first()
        if last_export_detail and last_export_detail.last_exported_at and last_export_detail.total_expense_groups_count:
            return Response(
                data=self.serializer_class(last_export_detail).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    'message': 'latest exported details does not exist in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class WorkspaceAdminsView(viewsets.ViewSet):

    def get(self, request, *args, **kwargs):
        """
        Get Admins for the workspaces
        """

        admin_email = get_workspace_admin(workspace_id=kwargs['workspace_id'])

        return Response(
                data=admin_email,
                status=status.HTTP_200_OK
            )
