import json
import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from fylesdk import exceptions as fyle_exc
from xerosdk import exceptions as xero_exc

from fyle_rest_auth.helpers import get_fyle_admin
from fyle_rest_auth.utils import AuthUtils
from fyle_rest_auth.models import AuthToken

from apps.workspaces.tasks import schedule_sync
from fyle_xero_api.utils import assert_valid

from apps.fyle.helpers import get_cluster_domain
from apps.fyle.models import ExpenseGroupSettings
from apps.fyle.utils import FyleConnector
from apps.xero.utils import XeroConnector
from apps.mappings.models import TenantMapping

from .models import Workspace, FyleCredential, XeroCredentials, WorkspaceGeneralSettings, WorkspaceSchedule
from .utils import generate_xero_identity, generate_xero_refresh_token, create_or_update_general_settings
from .serializers import WorkspaceSerializer, FyleCredentialSerializer, XeroCredentialSerializer, \
    WorkSpaceGeneralSettingsSerializer, WorkspaceScheduleSerializer

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

        workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

        if workspace:
            workspace.user.add(User.objects.get(user_id=request.user))
            cache.delete(str(workspace.id))
        else:
            workspace = Workspace.objects.create(name=org_name, fyle_org_id=org_id)

            ExpenseGroupSettings.objects.create(workspace_id=workspace.id)

            workspace.user.add(User.objects.get(user_id=request.user))

            auth_tokens = AuthToken.objects.get(user__user_id=request.user)

            cluster_domain = get_cluster_domain(auth_tokens.refresh_token)

            FyleCredential.objects.update_or_create(
                refresh_token=auth_tokens.refresh_token,
                workspace_id=workspace.id,
                cluster_domain=cluster_domain
            )

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


class ConnectFyleView(viewsets.ViewSet):
    """
    Fyle Connect Oauth View
    """
    def post(self, request, **kwargs):
        """
        Post of Fyle Credentials
        """
        try:
            authorization_code = request.data.get('code')

            workspace = Workspace.objects.get(id=kwargs['workspace_id'])

            tokens = auth_utils.generate_fyle_refresh_token(authorization_code)
            refresh_token = tokens['refresh_token']

            fyle_user = get_fyle_admin(tokens['access_token'], None)
            org_name = fyle_user['data']['org']['name']
            org_id = fyle_user['data']['org']['id']

            assert_valid(workspace.fyle_org_id and workspace.fyle_org_id == org_id,
                         'Please select the correct Fyle account - {0}'.format(workspace.name))

            workspace.name = org_name
            workspace.fyle_org_id = org_id
            workspace.save()

            cluster_domain = get_cluster_domain(refresh_token)

            fyle_credentials, _ = FyleCredential.objects.update_or_create(
                workspace_id=kwargs['workspace_id'],
                defaults={
                    'refresh_token': refresh_token,
                    'cluster_domain': cluster_domain
                }
            )

            return Response(
                data=FyleCredentialSerializer(fyle_credentials).data,
                status=status.HTTP_200_OK
            )
        except fyle_exc.UnauthorizedClientError:
            return Response(
                {
                    'message': 'Invalid Authorization Code'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except fyle_exc.NotFoundClientError:
            return Response(
                {
                    'message': 'Fyle Application not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except fyle_exc.WrongParamsError:
            return Response(
                {
                    'message': 'Some of the parameters are wrong'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except fyle_exc.InternalServerError:
            return Response(
                {
                    'message': 'Wrong/Expired Authorization code'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, **kwargs):
        """Delete credentials"""
        workspace_id = kwargs['workspace_id']
        FyleCredential.objects.filter(workspace_id=workspace_id).delete()

        return Response(data={
            'workspace_id': workspace_id,
            'message': 'Fyle credentials deleted'
        })

    def get(self, request, **kwargs):
        """
        Get Fyle Credentials in Workspace
        """
        try:
            workspace = Workspace.objects.get(pk=kwargs['workspace_id'])
            fyle_credentials = FyleCredential.objects.get(workspace=workspace)

            if fyle_credentials:
                return Response(
                    data=FyleCredentialSerializer(fyle_credentials).data,
                    status=status.HTTP_200_OK
                )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle Credentials not found in this workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
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

            refresh_token = generate_xero_refresh_token(authorization_code)

            xero_credentials = XeroCredentials.objects.filter(workspace_id=kwargs['workspace_id']).first()
            tenant_mapping = TenantMapping.objects.filter(workspace_id=kwargs['workspace_id']).first()

            if not xero_credentials:
                xero_credentials = XeroCredentials.objects.create(
                    refresh_token=refresh_token,
                    workspace_id=kwargs['workspace_id']
                )

            else:
                xero_credentials.refresh_token = refresh_token
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
                    xero_credentials.country = company_info['CountryCode']
                    xero_credentials.save()

                except xero_exc.WrongParamsError as exception:
                    logger.error(exception.response)

            return Response(
                data=XeroCredentialSerializer(xero_credentials).data,
                status=status.HTTP_200_OK
            )
        except xero_exc.InvalidClientError as e:
            return Response(
                json.loads(e.response),
                status=status.HTTP_400_BAD_REQUEST
            )
        except xero_exc.InvalidGrant as e:
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

    def delete(self, request, **kwargs):
        """Delete credentials"""
        workspace_id = kwargs['workspace_id']
        XeroCredentials.objects.filter(workspace_id=workspace_id).delete()

        return Response(data={
            'workspace_id': workspace_id,
            'message': 'Xero credentials deleted'
        })

    def get(self, request, **kwargs):
        """
        Get Xero Credentials in Workspace
        """
        try:
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

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
        xero_credentials = XeroCredentials.objects.filter(workspace_id=kwargs['workspace_id']).first()
        tenant_mapping = TenantMapping.objects.filter(workspace_id=kwargs['workspace_id']).first()
        if xero_credentials:
            if tenant_mapping and tenant_mapping.connection_id:
                try:
                    xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])
                    xero_connector.connection.connections.remove_connection(tenant_mapping.connection_id)
                except (xero_exc.InvalidGrant, xero_exc.UnsupportedGrantType,
                        xero_exc.InvalidTokenError, xero_exc.UnsuccessfulAuthentication,
                        xero_exc.WrongParamsError, xero_exc.NoPrivilegeError,
                        xero_exc.InternalServerError):
                    pass
            xero_credentials.delete()

        return Response(
            data={
                'message': 'Revoked Xero connection'
            },
            status=status.HTTP_200_OK
        )

class ScheduleView(viewsets.ViewSet):
    """
    Schedule View
    """
    def post(self, request, **kwargs):
        """
        Post Settings
        """
        schedule_enabled = request.data.get('schedule_enabled')
        assert_valid(schedule_enabled is not None, 'Schedule enabled cannot be null')

        hours = request.data.get('hours')
        assert_valid(hours is not None, 'Hours cannot be left empty')

        settings = schedule_sync(
            workspace_id=kwargs['workspace_id'],
            schedule_enabled=schedule_enabled,
            hours=hours
        )

        return Response(
            data=WorkspaceScheduleSerializer(settings).data,
            status=status.HTTP_200_OK
        )

    def get(self, *args, **kwargs):
        try:
            ns_credentials = WorkspaceSchedule.objects.get(workspace_id=kwargs['workspace_id'])

            return Response(
                data=WorkspaceScheduleSerializer(ns_credentials).data,
                status=status.HTTP_200_OK
            )
        except WorkspaceSchedule.DoesNotExist:
            return Response(
                data={
                    'message': 'Schedule settings does not exist in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
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
        authorization_code = request.data.get('code')
        identity = generate_xero_identity(authorization_code)

        return Response(
            data=json.loads(identity),
            status=status.HTTP_200_OK
        )