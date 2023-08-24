from datetime import datetime, timezone

from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_accounting_mappings.models import DestinationAttribute
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer

from django_q.tasks import Chain

from .serializers import XeroFieldSerializer
from apps.exceptions import handle_view_exceptions

from .actions import get_xero_connector, sync_tenant, sync_dimensions, refersh_xero_dimension

class TokenHealthView(generics.RetrieveAPIView):
    """
    Token Health View
    """

    @handle_view_exceptions()
    def get(self, request, *args, **kwargs):
            
            get_xero_connector(workspace_id = self.kwargs['workspace_id'])

            return Response(
                status=status.HTTP_200_OK
            )


class TenantView(generics.ListCreateAPIView):
    """
    Tenant view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self, **kwargs):
        return DestinationAttribute.objects.filter(
            attribute_type='TENANT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Get tenants from Xero
        """

        tenants = sync_tenant(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data=self.serializer_class(tenants, many=True).data,
            status=status.HTTP_200_OK
        )


class XeroFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = XeroFieldSerializer

    def get_queryset(self):
        attributes = DestinationAttribute.objects.filter(
            ~Q(attribute_type='CONTACT') & ~Q(attribute_type='ACCOUNT') &
            ~Q(attribute_type='TENANT') & ~Q(attribute_type='BANK_ACCOUNT') & ~Q(attribute_type='TAX_CODE') & ~Q(attribute_type='CUSTOMER'),
            workspace_id=self.kwargs['workspace_id']
        ).values('attribute_type', 'display_name').distinct()

        return attributes


class SyncXeroDimensionView(generics.ListCreateAPIView):
    """
    Sync Xero Dimensions View
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync Data From Xero
        """

        sync_dimensions(workspace_id=self.kwargs['workspace_id'])
        
        return Response(
            status=status.HTTP_200_OK
        )


class RefreshXeroDimensionView(generics.ListCreateAPIView):
    """
    Refresh Xero Dimensions view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync data from Xero
        """

        refersh_xero_dimension(workspace_id=self.kwargs['workspace_id'])

        return Response(
            status=status.HTTP_200_OK
        )


class DestinationAttributesView(generics.ListAPIView):
    """
    Destination Attributes view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        attribute_types = self.request.query_params.get('attribute_types').split(',')
        active = self.request.query_params.get('active')
        workspace_id = self.kwargs['workspace_id']

        filters = {
            'attribute_type__in': attribute_types,
            'workspace_id':  workspace_id
        }

        if active and active.lower() == 'true':
            filters['active'] = True

        return DestinationAttribute.objects.filter(**filters).order_by('value')
