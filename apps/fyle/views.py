import logging

from django_filters.rest_framework import DjangoFilterBackend
from django_q.tasks import async_task
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from apps.fyle.actions import exportable_expense_group, get_expense_field
from apps.fyle.helpers import ExpenseGroupSearchFilter
from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.fyle.queue import handle_webhook_callback
from apps.fyle.serializers import ExpenseFieldSerializer, ExpenseGroupSerializer, ExpenseGroupSettingsSerializer
from apps.fyle.tasks import create_expense_groups, get_task_log_and_fund_source
from apps.workspaces.models import FeatureConfig, FyleCredential, Workspace
from fyle_xero_api.utils import LookupFieldMixin

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class ExpenseGroupView(LookupFieldMixin, generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """

    queryset = ExpenseGroup.objects.all().order_by("-updated_at").distinct()
    serializer_class = ExpenseGroupSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpenseGroupSearchFilter


class ExpenseGroupSettingsView(generics.RetrieveAPIView):
    """
    Expense Group Settings View
    """

    lookup_field = "workspace_id"
    lookup_url_kwarg = "workspace_id"
    serializer_class = ExpenseGroupSettingsSerializer
    queryset = ExpenseGroupSettings.objects.all()


class ExpenseFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = ExpenseFieldSerializer

    def get(self, request, *args, **kwargs):
        expense_fields = get_expense_field(workspace_id=kwargs["workspace_id"])

        return Response(expense_fields, status=status.HTTP_200_OK)


class ExpenseGroupSyncView(generics.CreateAPIView):
    """
    Create expense groups
    """

    def post(self, request, *args, **kwargs):
        """
        Post expense groups creation
        """
        task_log, fund_source = get_task_log_and_fund_source(kwargs["workspace_id"])

        create_expense_groups(workspace_id=kwargs["workspace_id"], fund_source=fund_source, task_log=task_log, imported_from=ExpenseImportSourceEnum.DASHBOARD_SYNC)

        return Response(status=status.HTTP_200_OK)


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        workspace = Workspace.objects.get(id=kwargs['workspace_id'])
        FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

        fyle_webhook_sync_enabled = FeatureConfig.get_feature_config(workspace_id=kwargs['workspace_id'], key='fyle_webhook_sync_enabled')
        if fyle_webhook_sync_enabled and workspace.source_synced_at is not None:
            logger.info(f"Skipping sync_dimensions for workspace {kwargs['workspace_id']} as webhook sync is enabled")
            return Response(status=status.HTTP_200_OK)

        async_task('apps.fyle.tasks.check_interval_and_sync_dimension', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class RefreshFyleDimensionView(generics.ListCreateAPIView):
    """
    Refresh Fyle Dimensions view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        Workspace.objects.get(id=kwargs['workspace_id'])
        FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

        async_task('apps.fyle.tasks.sync_dimensions', kwargs['workspace_id'])

        return Response(status=status.HTTP_200_OK)


class ExportableExpenseGroupsView(generics.RetrieveAPIView):
    """
    List Exportable Expense Groups
    """

    def get(self, request, *args, **kwargs):
        expense_group_ids = exportable_expense_group(
            workspace_id=kwargs["workspace_id"]
        )

        return Response(
            data={"exportable_expense_group_ids": expense_group_ids},
            status=status.HTTP_200_OK,
        )


class ExportView(generics.CreateAPIView):
    """
    Export View
    """
    authentication_classes = []
    permission_classes = []

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        handle_webhook_callback(request.data, int(kwargs['workspace_id']))

        return Response(data={}, status=status.HTTP_200_OK)
