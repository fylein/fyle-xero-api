from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from apps.exceptions import handle_view_exceptions
from apps.fyle.actions import exportable_expense_group, get_expense_field, refresh_fyle_dimension, sync_fyle_dimension
from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.fyle.serializers import ExpenseFieldSerializer, ExpenseGroupSerializer, ExpenseGroupSettingsSerializer
from apps.fyle.tasks import async_create_expense_groups, get_task_log_and_fund_source
from fyle_xero_api.utils import LookupFieldMixin
from apps.fyle.queue import async_import_and_export_expenses


class ExpenseGroupView(LookupFieldMixin, generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """

    serializer_class = ExpenseGroupSerializer
    queryset = ExpenseGroup.objects.filter().order_by(
        "-updated_at"
    )
    serializer_class = ExpenseGroupSerializer
    filterset_fields = {"exported_at": {"gte", "lte"}, "tasklog__status": {"exact"}}


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

        async_create_expense_groups(kwargs["workspace_id"], fund_source, task_log)

        return Response(status=status.HTTP_200_OK)


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync Data From Fyle
        """

        sync_fyle_dimension(workspace_id=kwargs["workspace_id"])

        return Response(status=status.HTTP_200_OK)


class RefreshFyleDimensionView(generics.ListCreateAPIView):
    """
    Refresh Fyle Dimensions view
    """

    @handle_view_exceptions()
    def post(self, request, *args, **kwargs):
        """
        Sync data from Fyle
        """

        refresh_fyle_dimension(workspace_id=kwargs["workspace_id"])

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

    def post(self, request, *args, **kwargs):
        async_import_and_export_expenses(request.data)

        return Response(data={}, status=status.HTTP_200_OK)
