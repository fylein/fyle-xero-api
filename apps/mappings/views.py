from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_xero_api.utils import assert_valid

from .serializers import TenantMappingSerializer
from .models import TenantMapping
from .utils import MappingUtils


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
