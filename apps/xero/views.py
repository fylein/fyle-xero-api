from django.db.models import Q
from apps.workspaces.models import Workspace, XeroCredentials
from django_filters.rest_framework import DjangoFilterBackend
from django_q.tasks import async_task
from fyle_accounting_mappings.models import DestinationAttribute
from fyle_accounting_mappings.serializers import DestinationAttributeSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from apps.xero.actions import sync_tenant
from apps.xero.serializers import XeroFieldSerializer
from fyle_xero_api.utils import LookupFieldMixin
from apps.xero.utils import XeroConnector
from xerosdk import exceptions as xero_exc
from apps.exceptions import invalidate_xero_credentials


class TokenHealthView(generics.RetrieveAPIView):
    """
    Token Health View
    """

    @handle_view_exceptions()
    def get(self, request, *args, **kwargs):
        status_code = status.HTTP_200_OK
        message = "Xero connection is active"

        workspace_id = kwargs.get('workspace_id')
        xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace_id).first()

        if not xero_credentials:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Xero credentials not found"
        elif xero_credentials.is_expired:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Xero connection expired"
        elif not xero_credentials.refresh_token:
            status_code = status.HTTP_400_BAD_REQUEST
            message = "Xero disconnected"
        else:
            try:
                xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)
                xero_connector.get_organisations()
            except (xero_exc.WrongParamsError, xero_exc.InvalidTokenError):
                invalidate_xero_credentials(workspace_id)
                status_code = status.HTTP_400_BAD_REQUEST
                message = "Xero connection expired"

        return Response({"message": message}, status=status_code)


class TenantView(LookupFieldMixin, generics.ListCreateAPIView):
    """
    Tenant view
    """

    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = {"attribute_type": {"exact"}}
    ordering_fields = ("value",)

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Get tenants from Xero
        """

        tenants = sync_tenant(workspace_id=self.kwargs["workspace_id"])

        return Response(
            data=self.serializer_class(tenants, many=True).data,
            status=status.HTTP_200_OK,
        )


class XeroFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = XeroFieldSerializer

    def get_queryset(self):
        attributes = (
            DestinationAttribute.objects.filter(
                ~Q(attribute_type="CONTACT")
                & ~Q(attribute_type="ACCOUNT")
                & ~Q(attribute_type="TENANT")
                & ~Q(attribute_type="BANK_ACCOUNT")
                & ~Q(attribute_type="TAX_CODE"),
                workspace_id=self.kwargs["workspace_id"],
            )
            .values("attribute_type", "display_name")
            .distinct()
        )

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

        # Check for a valid workspace and fyle creds and respond with 400 if not found
        Workspace.objects.get(id=kwargs['workspace_id'])
        XeroCredentials.get_active_xero_credentials(kwargs['workspace_id'])

        async_task('apps.xero.actions.sync_dimensions', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class RefreshXeroDimensionView(generics.ListCreateAPIView):
    """
    Refresh Xero Dimensions view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync data from Xero
        """

        # Check for a valid workspace and fyle creds and respond with 400 if not found
        Workspace.objects.get(id=kwargs['workspace_id'])
        XeroCredentials.get_active_xero_credentials(kwargs['workspace_id'])

        async_task('apps.xero.actions.refersh_xero_dimension', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class DestinationAttributesView(LookupFieldMixin, generics.ListAPIView):
    """
    Destination Attributes view
    """

    queryset = DestinationAttribute.objects.all()
    serializer_class = DestinationAttributeSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = {"attribute_type": {"exact", "in"}, "active": {"exact"}}
    ordering_fields = ("value",)
