import logging

from django_q.tasks import Chain
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_xero_api.utils import assert_valid

from xerosdk.exceptions import UnsuccessfulAuthentication

from .serializers import TenantMappingSerializer, GeneralMappingSerializer
from .models import TenantMapping, GeneralMapping
from apps.workspaces.models import XeroCredentials
from .utils import MappingUtils
from ..workspaces.models import WorkspaceGeneralSettings
from apps.xero.utils import XeroConnector
from apps.workspaces.models import Workspace

logger = logging.getLogger(__name__)


class TenantMappingView(generics.ListCreateAPIView):
    """
    Tenant mappings view
    """
    serializer_class = TenantMappingSerializer

    def post(self, request, *args, **kwargs):
        """
        Post Tenant mapping view
        """
        tenant_mapping_payload = request.data

        assert_valid(tenant_mapping_payload is not None, 'Request body is empty')

        mapping_utils = MappingUtils(kwargs['workspace_id'])
        tenant_mapping_object = mapping_utils.create_or_update_tenant_mapping(tenant_mapping_payload)
        xero_credentials = XeroCredentials.objects.filter(workspace_id=kwargs['workspace_id']).first()
        workspace = Workspace.objects.filter(id=kwargs['workspace_id']).first()

        try:
            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])
            tenant_mapping = TenantMapping.objects.filter(workspace_id=kwargs['workspace_id']).first()
            company_info = xero_connector.get_organisations()[0]
            workspace.xero_currency = company_info['BaseCurrency']
            workspace.save()
            xero_credentials.country = company_info['CountryCode']
            xero_credentials.save()

            if tenant_mapping and not tenant_mapping.connection_id:
                connections = xero_connector.connection.connections.get_all()
                connection = list(filter(lambda connection: connection['tenantId'] == tenant_mapping.tenant_id, connections))

                if connection:
                    tenant_mapping.connection_id = connection[0]['id']
                    tenant_mapping.save()

        except UnsuccessfulAuthentication:
            logger.info('Xero refresh token is invalid for workspace_id - %s', kwargs['workspace_id'])

        except Exception:
            logger.info('Error while fetching company information')

        return Response(
            data=self.serializer_class(tenant_mapping_object).data,
            status=status.HTTP_200_OK
        )

    def get(self, request, *args, **kwargs):
        """
        Get tenant mappings
        """
        try:
            subsidiary_mapping = TenantMapping.objects.get(workspace_id=kwargs['workspace_id'])

            return Response(
                data=self.serializer_class(subsidiary_mapping).data,
                status=status.HTTP_200_OK
            )
        except TenantMapping.DoesNotExist:
            return Response(
                {
                    'message': 'Tenant mappings do not exist for the workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AutoMapEmployeeView(generics.CreateAPIView):
    """
    Auto Map Employees view
    """

    def post(self, request, *args, **kwargs):
        """
        Trigger Auto Map employees
        """
        try:
            workspace_id = kwargs['workspace_id']
            general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

            chain = Chain()

            if not general_settings.auto_map_employees:
                return Response(
                    data={
                        'message': 'Employee mapping preference not found for this workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            chain.append(
                'apps.mappings.tasks.async_auto_map_employees', workspace_id)

            chain.run()

            return Response(
                data={},
                status=status.HTTP_200_OK
            )

        except GeneralMapping.DoesNotExist:
            return Response(
                {
                    'message': 'General mappings do not exist for this workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
