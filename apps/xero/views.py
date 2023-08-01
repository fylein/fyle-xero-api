from datetime import datetime, timezone

from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_accounting_mappings.models import DestinationAttribute, MappingSetting
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer

from xerosdk.exceptions import InvalidGrant, InvalidTokenError, UnsuccessfulAuthentication

from django_q.tasks import Chain

from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.workspaces.models import XeroCredentials, Workspace
from apps.workspaces.serializers import WorkspaceSerializer
from apps.xero.models import BankTransaction, Bill
from fyle_xero_api.utils import assert_valid

from .utils import XeroConnector
from .serializers import XeroFieldSerializer
from .tasks import create_bank_transaction, schedule_bank_transaction_creation, create_bill, schedule_bills_creation, \
    create_payment, check_xero_object_status, process_reimbursements, create_chain_and_export

from .actions import get_xero_credentials, get_accounts, get_contacts, get_items, get_tracking_categories, \
get_tenants, export_trigger, sync_xero_dimension, refresh_xero_dimension
from apps.exceptions import handle_view_exceptions

from fyle_xero_api.utils import LookupFieldMixin

class TokenHealthView(generics.RetrieveAPIView):
    """
    Token Health View
    """

    @handle_view_exceptions()
    def get(self, request, *args, **kwargs):            
            get_xero_credentials(workspace_id=kwargs['workspace_id'])

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

        tenants = get_tenants(workspace_id=kwargs['workspace_id'])

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

        sync_xero_dimension(workspace_id=kwargs['workspace_id'])

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

        workspace_id = kwargs['workspace_id']

        refresh_xero_dimension(workspace_id=workspace_id)        

        return Response(
            status=status.HTTP_200_OK
        )


class DestinationAttributesView(LookupFieldMixin, generics.ListAPIView):
    """
    Destination Attributes view
    """
    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    pagination_class = None
    filterset_fields = {'attribute_type': {'exact', 'in'}, 'display_name': {'exact', 'in'}, 'active': {'exact'}}
    ordering_fields = ('value',)
