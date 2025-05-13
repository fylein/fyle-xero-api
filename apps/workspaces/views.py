import logging

from django.contrib.auth import get_user_model
from apps.workspaces.tasks import post_to_integration_settings
from django_q.tasks import async_task
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_rest_auth.utils import AuthUtils
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import status

from apps.tasks.models import TaskLog
from apps.exceptions import handle_view_exceptions
from apps.workspaces.actions import connect_xero, export_to_xero, get_workspace_admin, post_workspace, revoke_connections
from apps.workspaces.models import LastExportDetail, Workspace, WorkspaceGeneralSettings, XeroCredentials
from apps.workspaces.serializers import (
    LastExportDetailSerializer,
    WorkSpaceGeneralSettingsSerializer,
    WorkspaceSerializer,
    XeroCredentialSerializer,
)
from apps.workspaces.utils import generate_xero_identity

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

        Workspace.objects.raw("Select 1 from workspaces_workspace")

        return Response(data={"message": "Ready"}, status=status.HTTP_200_OK)


class WorkspaceView(generics.CreateAPIView, generics.RetrieveUpdateAPIView):
    """
    Xero Workspace
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a Workspace
        """
        access_token = request.META.get("HTTP_AUTHORIZATION")
        workspace = post_workspace(access_token=access_token, request=request)

        return Response(
            data=WorkspaceSerializer(workspace).data, status=status.HTTP_200_OK
        )

    def get(self, request):
        """
        Get workspace
        """
        user = User.objects.get(user_id=request.user)
        org_id = request.query_params.get("org_id")
        workspaces = Workspace.objects.filter(user__in=[user], fyle_org_id=org_id).all()

        if workspaces:
            async_task(
                "apps.workspaces.tasks.async_update_workspace_name",
                workspaces[0],
                request.META.get("HTTP_AUTHORIZATION"),
                q_options={
                    'cluster': 'import'
                }
            )

        return Response(
            data=WorkspaceSerializer(workspaces, many=True).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, **kwargs):
        """
        PATCH workspace
        """
        workspace_instance = Workspace.objects.get(pk=kwargs["workspace_id"])
        serializer = WorkspaceSerializer(
            workspace_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)


class ConnectXeroView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    Xero Connect Oauth View
    """

    @handle_view_exceptions()
    def post(self, request, **kwargs):
        """
        Post of Xero Credentials
        """

        authorization_code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri")

        xero_credentials = connect_xero(
            authorization_code=authorization_code,
            redirect_uri=redirect_uri,
            workspace_id=kwargs["workspace_id"],
        )

        post_to_integration_settings(kwargs["workspace_id"], True)

        return Response(
            data=XeroCredentialSerializer(xero_credentials).data,
            status=status.HTTP_200_OK,
        )

    @handle_view_exceptions()
    def get(self, request, **kwargs):
        """
        Get Xero Credentials in Workspace
        """

        xero_credentials = XeroCredentials.objects.get(
            workspace_id=kwargs["workspace_id"],
            is_expired=False,
            refresh_token__isnull=False,
        )

        return Response(
            data=XeroCredentialSerializer(xero_credentials).data,
            status=status.HTTP_200_OK,
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
        revoke_connections(workspace_id=kwargs["workspace_id"])
        post_to_integration_settings(kwargs["workspace_id"], False)

        return Response(
            data={"message": "Revoked Xero connection"}, status=status.HTTP_200_OK
        )


class GeneralSettingsView(generics.RetrieveUpdateAPIView):
    """
    General Settings
    """

    lookup_field = "workspace_id"
    lookup_url_kwarg = "workspace_id"
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

        authorization_code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri")
        identity = generate_xero_identity(authorization_code, redirect_uri)

        return Response(data=identity, status=status.HTTP_200_OK)


class ExportToXeroView(generics.CreateAPIView):
    """
    Export Expenses to QBO
    """

    def post(self, request, *args, **kwargs):
        export_to_xero(workspace_id=kwargs["workspace_id"], triggered_by=ExpenseImportSourceEnum.DASHBOARD_SYNC)

        return Response(status=status.HTTP_200_OK)


class LastExportDetailView(generics.RetrieveAPIView):
    """
    Last Export Details
    """

    lookup_field = "workspace_id"
    lookup_url_kwarg = "workspace_id"
    serializer_class = LastExportDetailSerializer
    queryset = LastExportDetail.objects.filter(
        last_exported_at__isnull=False, total_expense_groups_count__gt=0
    )

    def get_queryset(self):
        return super().get_queryset()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = serializer.data

        start_date = request.query_params.get('start_date')

        if start_date and response_data:
            workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=kwargs['workspace_id'])

            task_log_types = []
            if workspace_general_settings.reimbursable_expenses_object:
                task_log_types.append('CREATING_BILL')
            if workspace_general_settings.corporate_credit_card_expenses_object:
                task_log_types.append('CREATING_BANK_TRANSACTION')

            task_logs = TaskLog.objects.filter(
                workspace_id=kwargs['workspace_id'],
                updated_at__gte=start_date,
                status='COMPLETE',
                type__in=task_log_types
            ).order_by('-updated_at')

            successful_count = task_logs.count()

            failed_count = TaskLog.objects.filter(
                status__in=['FAILED', 'FATAL'],
                workspace_id=kwargs['workspace_id'],
                type__in=task_log_types
            ).count()

            response_data.update({
                'repurposed_successful_count': successful_count,
                'repurposed_failed_count': failed_count,
                'repurposed_last_exported_at': task_logs.last().updated_at if task_logs.last() else None
            })

        return Response(response_data)


class WorkspaceAdminsView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        """
        Get Admins for the workspaces
        """

        admin_email = get_workspace_admin(workspace_id=kwargs["workspace_id"])

        return Response(data=admin_email, status=status.HTTP_200_OK)
