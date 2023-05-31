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


class TokenHealthView(generics.RetrieveAPIView):
    """
    Token Health View
    """

    def get(self, request, *args, **kwargs):
        try:
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])
            XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            return Response(
                status=status.HTTP_200_OK
            )

        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except (InvalidGrant, UnsuccessfulAuthentication, InvalidTokenError) as e:
            if xero_credentials:
                xero_credentials.refresh_token = None
                xero_credentials.country = None
                xero_credentials.is_expired = True
                xero_credentials.save()
            return Response(
                data={
                    'message': 'Xero connection expired'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AccountView(generics.ListCreateAPIView):
    """
    Account view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='ACCOUNT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get accounts from Xero
        """
        try:
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])

            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            accounts = xero_connector.sync_accounts()

            return Response(
                data=self.serializer_class(accounts, many=True).data,
                status=status.HTTP_200_OK
            )
        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BankAccountView(generics.ListCreateAPIView):
    """
    BankAccount view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='BANK_ACCOUNT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        return Response(
            data={
                'message': 'Method Not Allowed'
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class ContactView(generics.ListCreateAPIView):
    """
    Contact view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='CONTACT', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get contacts from Xero
        """
        try:
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])

            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            contacts = xero_connector.sync_contacts()

            return Response(
                data=self.serializer_class(contacts, many=True).data,
                status=status.HTTP_200_OK
            )
        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ItemView(generics.ListCreateAPIView):
    """
    Item view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='ITEM', workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get items from Xero
        """
        try:
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])

            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            items = xero_connector.sync_items()

            return Response(
                data=self.serializer_class(items, many=True).data,
                status=status.HTTP_200_OK
            )
        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class TrackingCategoryView(generics.ListCreateAPIView):
    """
    Tracking Category view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        attribute_type = self.request.query_params.get('attribute_type')

        return DestinationAttribute.objects.filter(
            attribute_type=attribute_type, workspace_id=self.kwargs['workspace_id']).order_by('value')

    def post(self, request, *args, **kwargs):
        """
        Get Tracking Categories from Xero
        """
        try:
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])

            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            expense_custom_field_attributes = xero_connector.sync_tracking_categories()

            return Response(
                data=self.serializer_class(expense_custom_field_attributes, many=True).data,
                status=status.HTTP_200_OK
            )
        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
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

    def post(self, request, *args, **kwargs):
        """
        Get tenants from Xero
        """
        try:
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=kwargs['workspace_id'])

            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            tenants = xero_connector.sync_tenants()

            return Response(
                data=self.serializer_class(tenants, many=True).data,
                status=status.HTTP_200_OK
            )
        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ExportsTriggerView(generics.CreateAPIView):
    """
    Schedule Exports creation
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])
        chaining_attributes = []

        if expense_group_ids['personal']:
            chaining_attributes.extend(schedule_bills_creation(kwargs['workspace_id'], expense_group_ids['personal']))
        if expense_group_ids['ccc']:
            chaining_attributes.extend(schedule_bank_transaction_creation(kwargs['workspace_id'], expense_group_ids['ccc']))

        if chaining_attributes:
            create_chain_and_export(chaining_attributes, kwargs['workspace_id'])

        return Response(
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

    def post(self, request, *args, **kwargs):
        """
        Sync Data From Xero
        """
        try:
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

        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero Credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except (InvalidGrant, UnsuccessfulAuthentication, InvalidTokenError):
            return Response(
                data={
                    'message': 'Xero Credentials are invalid'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshXeroDimensionView(generics.ListCreateAPIView):
    """
    Refresh Xero Dimensions view
    """

    def post(self, request, *args, **kwargs):
        """
        Sync data from Xero
        """
        try:
            workspace_id = kwargs['workspace_id']
            xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id=workspace_id)
            xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)

            mapping_settings = MappingSetting.objects.filter(workspace_id=workspace_id, import_to_fyle=True)
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
            
            if chain.length() > 0:
                chain.run()

            xero_connector.sync_dimensions(workspace_id)

            workspace = Workspace.objects.get(id=workspace_id)
            workspace.destination_synced_at = datetime.now()
            workspace.save(update_fields=['destination_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )
        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except (InvalidGrant, UnsuccessfulAuthentication, InvalidTokenError):
            return Response(
                data={
                    'message': 'Xero credentials are invalid'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class PaymentView(generics.CreateAPIView):
    """
    Create Payment View
    """

    def post(self, request, *args, **kwargs):
        """
        Create payment
        """
        create_payment(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class ReimburseXeroPaymentsView(generics.CreateAPIView):
    """
    Reimburse Xero Payments View
    """

    def post(self, request, *args, **kwargs):
        """
        Process Reimbursements in Fyle
        """
        check_xero_object_status(workspace_id=self.kwargs['workspace_id'])
        process_reimbursements(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data={},
            status=status.HTTP_200_OK
        )

class TaxCodeView(generics.ListCreateAPIView):
    """
    Tax code API View
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return DestinationAttribute.objects.filter(
            attribute_type='TAX_CODE', workspace_id=self.kwargs['workspace_id']).order_by('value')


class DestinationAttributesView(generics.ListAPIView):
    """
    Destination Attributes view
    """
    serializer_class = DestinationAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        attribute_types = self.request.query_params.get('attribute_types').split(',')

        return DestinationAttribute.objects.filter(
            attribute_type__in=attribute_types, workspace_id=self.kwargs['workspace_id']).order_by('value')
