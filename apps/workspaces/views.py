import json
import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache

from django_q.tasks import async_task

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from fyle.platform import exceptions as fyle_exc
from apps.workspaces.signals import post_delete_xero_connection
from xerosdk import exceptions as xero_exc

from fyle_rest_auth.helpers import get_fyle_admin
from fyle_rest_auth.utils import AuthUtils
from fyle_rest_auth.models import AuthToken

from apps.workspaces.tasks import schedule_sync
from fyle_xero_api.utils import assert_valid

from apps.fyle.helpers import get_cluster_domain
from apps.fyle.models import ExpenseGroupSettings
from apps.xero.utils import XeroConnector
from apps.mappings.models import TenantMapping
from fyle_accounting_mappings.models import ExpenseAttribute

from .models import Workspace, FyleCredential, XeroCredentials, WorkspaceGeneralSettings, WorkspaceSchedule, LastExportDetail
from .utils import generate_xero_identity, generate_xero_refresh_token, create_or_update_general_settings
from .serializers import WorkspaceSerializer, FyleCredentialSerializer, XeroCredentialSerializer, \
    WorkSpaceGeneralSettingsSerializer, WorkspaceScheduleSerializer, LastExportDetailSerializer
from .tasks import export_to_xero

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
        fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
        org_name = fyle_user['data']['org']['name']
        org_id = fyle_user['data']['org']['id']
        fyle_currency = fyle_user['data']['org']['currency']

        workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

        if workspace:
            workspace.user.add(User.objects.get(user_id=request.user))
            cache.delete(str(workspace.id))
        else:
            workspace = Workspace.objects.create(name=org_name, fyle_currency=fyle_currency, fyle_org_id=org_id)

            ExpenseGroupSettings.objects.create(workspace_id=workspace.id)

            LastExportDetail.objects.create(workspace_id=workspace.id)

            workspace.user.add(User.objects.get(user_id=request.user))

            auth_tokens = AuthToken.objects.get(user__user_id=request.user)

            cluster_domain = get_cluster_domain(auth_tokens.refresh_token)

            FyleCredential.objects.update_or_create(
                refresh_token=auth_tokens.refresh_token,
                workspace_id=workspace.id,
                cluster_domain=cluster_domain
            )

            async_task('apps.workspaces.tasks.async_add_admins_to_workspace', workspace.id, request.user.user_id)

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

    def get_by_id(self, request, **kwargs):
        """
        Get Workspace by id
        """
        try:
            user = User.objects.get(user_id=request.user)
            workspace = Workspace.objects.get(pk=kwargs['workspace_id'], user=user)

            return Response(
                data=WorkspaceSerializer(workspace).data if workspace else {},
                status=status.HTTP_200_OK
            )
        except Workspace.DoesNotExist:
            return Response(
                data={
                    'message': 'Workspace with this id does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
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
    def post(self, request, **kwargs):
        """
        Post of Xero Credentials
        """
        try:
            authorization_code = request.data.get('code')
            redirect_uri = request.data.get('redirect_uri')
            if redirect_uri:
                refresh_token = generate_xero_refresh_token(authorization_code, redirect_uri)
            else:
                refresh_token = generate_xero_refresh_token(authorization_code)
            xero_credentials = XeroCredentials.objects.filter(workspace_id=kwargs['workspace_id']).first()
            tenant_mapping = TenantMapping.objects.filter(workspace_id=kwargs['workspace_id']).first()

            workspace = Workspace.objects.get(pk=kwargs['workspace_id'])

            if not xero_credentials:
                xero_credentials = XeroCredentials.objects.create(
                    refresh_token=refresh_token,
                    workspace_id=kwargs['workspace_id']
                )

            else:
                xero_credentials.refresh_token = refresh_token
                xero_credentials.is_expired = False
                xero_credentials.save()

            if tenant_mapping and not tenant_mapping.connection_id:
                xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])
                connections = xero_connector.connection.connections.get_all()
                connection = list(filter(lambda connection: connection['tenantId'] == tenant_mapping.tenant_id, connections))

                if connection:
                    tenant_mapping.connection_id = connection[0]['id']
                    tenant_mapping.save()
                    
            if tenant_mapping:
                try:
                    xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])
                    company_info = xero_connector.get_organisations()[0]
                    workspace.xero_currency = company_info['BaseCurrency']
                    workspace.save()
                    xero_credentials.country = company_info['CountryCode']
                    xero_credentials.save()

                except (xero_exc.WrongParamsError, xero_exc.UnsuccessfulAuthentication) as exception:
                    logger.info(exception.response)
            
            if workspace.onboarding_state == 'CONNECTION':
                workspace.onboarding_state = 'EXPORT_SETTINGS'
                workspace.save()

            return Response(
                data=XeroCredentialSerializer(xero_credentials).data,
                status=status.HTTP_200_OK
            )
        except (xero_exc.InvalidClientError, xero_exc.InvalidGrant, xero_exc.UnsuccessfulAuthentication) as e:
            return Response(
                json.loads(e.response),
                status=status.HTTP_400_BAD_REQUEST
            )
        except xero_exc.InvalidTokenError:
            return Response(
                {
                    'message': 'Invalid Authorization Code'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except xero_exc.InternalServerError:
            return Response(
                {
                    'message': 'Internal server error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    def get(self, request, **kwargs):
        """
        Get Xero Credentials in Workspace
        """
        try:
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'], is_expired=False, refresh_token__isnull=False)

            return Response(
                data=XeroCredentialSerializer(xero_credentials).data,
                status=status.HTTP_200_OK
            )
        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero Credentials not found in this workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
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
        workspace_id = kwargs['workspace_id']
        xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace_id).first()
        tenant_mapping = TenantMapping.objects.filter(workspace_id=workspace_id).first()
        if xero_credentials:
            if tenant_mapping and tenant_mapping.connection_id:
                try:
                    xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)
                    xero_connector.connection.connections.remove_connection(tenant_mapping.connection_id)
                except (xero_exc.InvalidGrant, xero_exc.UnsupportedGrantType,
                        xero_exc.InvalidTokenError, xero_exc.UnsuccessfulAuthentication,
                        xero_exc.WrongParamsError, xero_exc.NoPrivilegeError,
                        xero_exc.InternalServerError):
                    pass
            
            xero_credentials.refresh_token = None
            xero_credentials.country = None
            xero_credentials.is_expired = True
            xero_credentials.save()

            post_delete_xero_connection(workspace_id)

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

    def get(self, request, *args, **kwargs):
        """
        Get workspace general settings
        """
        try:
            general_settings = self.queryset.get(workspace_id=kwargs['workspace_id'])
            return Response(
                data=self.serializer_class(general_settings).data,
                status=status.HTTP_200_OK
            )
        except WorkspaceGeneralSettings.DoesNotExist:
            return Response(
                {
                    'message': 'General Settings does not exist in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
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

    def post(self, request, **kwargs):
        """
        Post Xero External Sign Ups
        """
        try:
            authorization_code = request.data.get('code')
            redirect_uri = request.data.get('redirect_uri')
            identity = generate_xero_identity(authorization_code, redirect_uri)

            return Response(
                data=identity,
                status=status.HTTP_200_OK
            )
        except Exception as exception:
            logger.info('Error while generating xero identity: %s', exception.__dict__)
            return Response(
                data={
                    'message': 'Error while generating xero identity'
                },
                status=status.HTTP_400_BAD_REQUEST
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

        workspace = Workspace.objects.get(pk=kwargs['workspace_id'])
        
        admin_email = []
        users = workspace.user.all()
        for user in users:
            admin = User.objects.get(user_id=user)
            employee = ExpenseAttribute.objects.filter(value=admin.email, workspace_id=kwargs['workspace_id'], attribute_type='EMPLOYEE').first()
            if employee:
                admin_email.append({'name': employee.detail['full_name'], 'email': admin.email})

        return Response(
                data=admin_email,
                status=status.HTTP_200_OK
            )
