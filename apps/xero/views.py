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
from apps.workspaces.models import XeroCredentials, Workspace, WorkspaceGeneralSettings
from apps.workspaces.serializers import WorkspaceSerializer
from apps.xero.models import BankTransaction, Bill
from fyle_xero_api.utils import assert_valid

from .utils import XeroConnector
from .serializers import XeroFieldSerializer
from .tasks import create_bank_transaction, schedule_bank_transaction_creation, create_bill, schedule_bills_creation, \
    create_payment, check_xero_object_status, process_reimbursements, create_chain_and_export
from apps.exceptions import handle_view_exceptions

class TokenHealthView(generics.RetrieveAPIView):
    """
    Token Health View
    """

    @handle_view_exceptions()
    def get(self, request, *args, **kwargs):
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])
            XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

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
        
        xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])

        xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

        tenants = xero_connector.sync_tenants()

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

        workspace = Workspace.objects.get(id=kwargs['workspace_id'])
        if workspace.destination_synced_at:
            time_interval = datetime.now(timezone.utc) - workspace.destination_synced_at

        if workspace.destination_synced_at is None or time_interval.days > 0:
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])
            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            xero_connector.sync_dimensions(kwargs['workspace_id'])

            workspace.destination_synced_at = datetime.now()
            workspace.save(update_fields=['destination_synced_at'])

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
        xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
        xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)

        mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id, import_to_fyle=True)
        workspace_general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
        chain = Chain()

        for mapping_setting in mapping_settings:
            if mapping_setting.source_field == 'PROJECT':
                # run auto_import_and_map_fyle_fields
                chain.append('apps.mappings.tasks.auto_import_and_map_fyle_fields', int(workspace_id))
            elif mapping_setting.source_field == 'COST_CENTER':
                # run auto_create_cost_center_mappings
                chain.append('apps.mappings.tasks.auto_create_cost_center_mappings', int(workspace_id))
            elif mapping_setting.is_custom:
                # run async_auto_create_custom_field_mappings
                chain.append('apps.mappings.tasks.async_auto_create_custom_field_mappings', int(workspace_id))
            elif workspace_general_settings.import_suppliers_as_merchants:
                # run auto_create_suppliers_as_merchants
                chain.append('apps.mappings.tasks.auto_create_suppliers_as_merchants', workspace_id)
        
        if chain.length() > 0:
            chain.run()

        xero_connector.sync_dimensions(workspace_id)

        workspace = Workspace.objects.get(id=workspace_id)
        workspace.destination_synced_at = datetime.now()
        workspace.save(update_fields=['destination_synced_at'])

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
