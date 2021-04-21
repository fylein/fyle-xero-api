import logging
from datetime import datetime, timezone

from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_accounting_mappings.models import DestinationAttribute
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer

from xerosdk.exceptions import InvalidGrant, InvalidTokenError, UnsuccessfulAuthentication

from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.workspaces.models import XeroCredentials, Workspace
from apps.workspaces.serializers import WorkspaceSerializer
from apps.xero.models import BankTransaction, Bill
from fyle_xero_api.utils import assert_valid

from .utils import XeroConnector
from .serializers import XeroFieldSerializer, BankTransactionSerializer, BillSerializer
from .tasks import create_bank_transaction, schedule_bank_transaction_creation, create_bill, schedule_bills_creation, \
    create_payment, check_xero_object_status, process_reimbursements

logger = logging.getLogger(__name__)


class OrganisationView(generics.RetrieveAPIView):
    """
    Organisation View
    """

    def get(self, request, *args, **kwargs):
        try:
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            organisations = xero_connector.get_organisations()

            return Response(
                data=organisations,
                status=status.HTTP_200_OK
            )

        except XeroCredentials.DoesNotExist:
            return Response(
                data={
                    'message': 'Xero credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except InvalidGrant as e:
            return Response(
                data={
                    'message': 'Xero connection expired'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except InvalidTokenError as e:
            return Response(
                data={
                    'message': 'Xero connection expired'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except UnsuccessfulAuthentication as e:
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
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

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
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

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
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

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
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

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
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

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


class BankTransactionView(generics.ListCreateAPIView):
    """
    Create BankTransaction
    """
    serializer_class = BankTransactionSerializer

    def get_queryset(self):
        return BankTransaction.objects.filter(
            expense_group__workspace_id=self.kwargs['workspace_id']
        ).order_by('-updated_at')

    def post(self, request, *args, **kwargs):
        """
        Create BankTransaction from expense group
        """
        expense_group_id = request.data.get('expense_group_id')
        task_log_id = request.data.get('task_log_id')

        assert_valid(expense_group_id is not None, 'Expense ids not found')
        assert_valid(task_log_id is not None, 'Task Log id not found')

        expense_group = ExpenseGroup.objects.get(pk=expense_group_id)
        task_log = TaskLog.objects.get(pk=task_log_id)

        create_bank_transaction(expense_group, task_log)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class BankTransactionScheduleView(generics.CreateAPIView):
    """
    Schedule BankTransaction creation
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])

        schedule_bank_transaction_creation(
            kwargs['workspace_id'], expense_group_ids)

        return Response(
            status=status.HTTP_200_OK
        )


class BillView(generics.ListCreateAPIView):
    """
    Create Bill
    """
    serializer_class = BillSerializer

    def get_queryset(self):
        return Bill.objects.filter(
            expense_group__workspace_id=self.kwargs['workspace_id']
        ).order_by('-updated_at')

    def post(self, request, *args, **kwargs):
        """
        Create Bill from expense group
        """
        expense_group_id = request.data.get('expense_group_id')
        task_log_id = request.data.get('task_log_id')

        assert_valid(expense_group_id is not None, 'Expense group id not found')
        assert_valid(task_log_id is not None, 'Task Log id not found')

        expense_group = ExpenseGroup.objects.get(pk=expense_group_id)
        task_log = TaskLog.objects.get(pk=task_log_id)

        create_bill(expense_group, task_log)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )


class BillScheduleView(generics.CreateAPIView):
    """
    Schedule Bill creation
    """

    def post(self, request, *args, **kwargs):
        expense_group_ids = request.data.get('expense_group_ids', [])

        schedule_bills_creation(kwargs['workspace_id'], expense_group_ids)

        return Response(
            status=status.HTTP_200_OK
        )


class XeroFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = XeroFieldSerializer

    def get_queryset(self):
        attributes = DestinationAttribute.objects.filter(
            ~Q(attribute_type='CONTACT') & ~Q(attribute_type='ACCOUNT') &
            ~Q(attribute_type='TENANT') & ~Q(attribute_type='BANK_ACCOUNT'),
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
                xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])
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


class RefreshXeroDimensionView(generics.ListCreateAPIView):
    """
    Refresh Xero Dimensions view
    """

    def post(self, request, *args, **kwargs):
        """
        Sync data from Xero
        """
        try:
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])
            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            xero_connector.sync_dimensions(kwargs['workspace_id'])

            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
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
