import logging

from django_q.tasks import Chain
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_xero_api.utils import assert_valid

from .serializers import TenantMappingSerializer, GeneralMappingSerializer
from .models import TenantMapping, GeneralMapping
from apps.workspaces.models import XeroCredentials
from .utils import MappingUtils
from ..workspaces.models import WorkspaceGeneralSettings
from apps.xero.utils import XeroConnector

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

        try:
            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])
            company_info = xero_connector.get_organisations()[0]
            xero_credentials.country = company_info['CountryCode']
            xero_credentials.save()

        except:
            logger.error("Error while fetching company information")

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


class GeneralMappingView(generics.ListCreateAPIView):
    """
    General mappings view
    """
    serializer_class = GeneralMappingSerializer

    def post(self, request, *args, **kwargs):
        """
        Post General mapping view
        """
        general_mapping_payload = request.data

        assert_valid(general_mapping_payload is not None, 'Request body is empty')

        mapping_utils = MappingUtils(kwargs['workspace_id'])
        general_mapping_object = mapping_utils.create_or_update_general_mapping(general_mapping_payload)

        return Response(
            data=self.serializer_class(general_mapping_object).data,
            status=status.HTTP_200_OK
        )

    def get(self, request, *args, **kwargs):
        """
        Get general mappings
        """
        try:
            general_mapping = GeneralMapping.objects.get(workspace_id=kwargs['workspace_id'])

            return Response(
                data=self.serializer_class(general_mapping).data,
                status=status.HTTP_200_OK
            )
        except GeneralMapping.DoesNotExist:
            return Response(
                {
                    'message': 'General mappings do not exist for the workspace'
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
