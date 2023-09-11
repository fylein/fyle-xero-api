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
from rest_framework import generics

logger = logging.getLogger(__name__)


User = get_user_model()
auth_utils = AuthUtils()


class ReadyView(generics.ListAPIView):
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


class WorkspaceView(generics.CreateAPIView, generics.RetrieveUpdateAPIView):
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


class ConnectXeroView(generics.CreateAPIView, generics.RetrieveAPIView):
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
    

class RevokeXeroConnectionView(generics.CreateAPIView):
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


class GeneralSettingsView(generics.RetrieveAPIView):
    """
    General Settings
    """
    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'
    serializer_class = WorkSpaceGeneralSettingsSerializer
    queryset = WorkspaceGeneralSettings.objects.all()

    

class XeroExternalSignUpsView(generics.CreateAPIView):
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


class ExportToXeroView(generics.CreateAPIView):
    """
    Export Expenses to QBO
    """

    def post(self, request, *args, **kwargs):
        export_to_xero(workspace_id=kwargs['workspace_id'])

        return Response(
            status=status.HTTP_200_OK
        )


class LastExportDetailView(generics.RetrieveAPIView):
    """
    Last Export Details
    """

    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'
    serializer_class = LastExportDetailSerializer
    queryset = LastExportDetail.objects.filter(last_exported_at__isnull=False, total_expense_groups_count__gt=0)
    

class WorkspaceAdminsView(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        """
        Get Admins for the workspaces
        """

        admin_email = get_workspace_admin(workspace_id=kwargs['workspace_id'])

        return Response(
                data=admin_email,
                status=status.HTTP_200_OK
            )
