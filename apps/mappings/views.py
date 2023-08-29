import logging

from django_q.tasks import Chain
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_xero_api.utils import assert_valid

from .serializers import TenantMappingSerializer
from .models import TenantMapping
from ..workspaces.models import WorkspaceGeneralSettings
from apps.exceptions import handle_view_exceptions
from .actions import tenant_mapping_view

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

        tenant_mapping_object = tenant_mapping_view(workspace_id=kwargs['workspace_id'],tenant_mapping_payload=tenant_mapping_payload)

        return Response(
            data=self.serializer_class(tenant_mapping_object).data,
            status=status.HTTP_200_OK
        )

    @handle_view_exceptions()
    def get(self, request, *args, **kwargs):
        """
        Get tenant mappings
        """

        subsidiary_mapping = TenantMapping.objects.get(workspace_id=kwargs['workspace_id'])

        return Response(
            data=self.serializer_class(subsidiary_mapping).data,
            status=status.HTTP_200_OK
        )


class AutoMapEmployeeView(generics.CreateAPIView):
    """
    Auto Map Employees view
    """
    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Trigger Auto Map employees
        """
    
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
