import logging

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_accounting_mappings.models import DestinationAttribute
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer

from apps.workspaces.models import XeroCredentials

from .utils import XeroConnector

logger = logging.getLogger(__name__)


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
        Get accounts from NetSuite
        """
        try:
            xero_credentials = XeroCredentials.objects.get(workspace_id=kwargs['workspace_id'])

            xero_connector = XeroConnector(xero_credentials, workspace_id=kwargs['workspace_id'])

            accounts = xero_connector.sync_accounts(account_type='ACCOUNT')

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
