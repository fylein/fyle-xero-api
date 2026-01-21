import logging

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from apps.mappings.actions import create_tenant_mapping
from apps.mappings.models import TenantMapping
from apps.mappings.serializers import TenantMappingSerializer
from apps.workspaces.models import WorkspaceGeneralSettings
from fyle_xero_api.utils import assert_valid
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq

logger = logging.getLogger(__name__)


class TenantMappingView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    Tenant mappings view
    """

    lookup_field = 'workspace_id'
    lookup_url_kwarg = 'workspace_id'
    serializer_class = TenantMappingSerializer
    queryset = TenantMapping.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Post Tenant mapping view
        """
        tenant_mapping_payload = request.data

        assert_valid(tenant_mapping_payload is not None, 'Request body is empty')

        tenant_mapping_object = create_tenant_mapping(
            workspace_id=kwargs['workspace_id'],
            tenant_mapping_payload=tenant_mapping_payload,
        )

        return Response(
            data=self.serializer_class(tenant_mapping_object).data,
            status=status.HTTP_200_OK,
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

        workspace_id = kwargs["workspace_id"]
        general_settings = WorkspaceGeneralSettings.objects.get(
            workspace_id=workspace_id
        )

        if not general_settings.auto_map_employees:
            return Response(
                data={
                    "message": "Employee mapping preference not found for this workspace"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            'workspace_id': workspace_id,
            'action': WorkerActionEnum.AUTO_MAP_EMPLOYEES.value,
            'data': {
                'workspace_id': workspace_id
            }
        }
        publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.IMPORT.value)

        return Response(data={}, status=status.HTTP_200_OK)
