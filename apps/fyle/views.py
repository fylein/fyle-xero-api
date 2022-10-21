from datetime import datetime, timezone
from django.db.models import Q

from rest_framework.views import status
from rest_framework import generics
from rest_framework.response import Response

from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_accounting_mappings.serializers import ExpenseAttributeSerializer

from fyle_integrations_platform_connector import PlatformConnector

from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, Workspace
from apps.workspaces.serializers import WorkspaceSerializer

from fyle_integrations_platform_connector import PlatformConnector
from .tasks import create_expense_groups, schedule_expense_group_creation, get_task_log_and_fund_source, async_create_expense_groups
from .models import Expense, ExpenseGroup, ExpenseGroupSettings
from .serializers import ExpenseGroupSerializer, ExpenseSerializer, ExpenseFieldSerializer, \
    ExpenseGroupSettingsSerializer


class ExpenseGroupView(generics.ListCreateAPIView):
    """
    List Fyle Expenses
    """
    serializer_class = ExpenseGroupSerializer

    def get_queryset(self):
        state = self.request.query_params.get('state', 'ALL')
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        exported_at = self.request.query_params.get('exported_at', None)
        expense_group_ids = self.request.query_params.get('expense_group_ids', None)

        if expense_group_ids:
            return ExpenseGroup.objects.filter(
                workspace_id=self.kwargs['workspace_id'],
                id__in=expense_group_ids.split(',')
            )

        if state == 'ALL':
            return ExpenseGroup.objects.filter(workspace_id=self.kwargs['workspace_id']).order_by('-updated_at')

        if state == 'FAILED':
            return ExpenseGroup.objects.filter(tasklog__status='FAILED',
                                               workspace_id=self.kwargs['workspace_id']).order_by('-updated_at')

        elif state == 'COMPLETE':
            filters = {
                'workspace_id': self.kwargs['workspace_id'],
                'tasklog__status': 'COMPLETE'
            }

            if start_date and end_date:
                filters['exported_at__range'] = [start_date, end_date]

            if exported_at:
                filters['exported_at__gte'] = exported_at

            return ExpenseGroup.objects.filter(**filters).order_by('-exported_at')

        elif state == 'READY':
            return ExpenseGroup.objects.filter(
                workspace_id=self.kwargs['workspace_id'],
                bill__id__isnull=True,
                banktransaction__id__isnull=True
            ).order_by('-updated_at')

    def post(self, request, *args, **kwargs):
        """
        Create expense groups
        """
        task_log = TaskLog.objects.get(pk=request.data.get('task_log_id'))

        general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=kwargs['workspace_id'])

        fund_source = ['PERSONAL']
        if general_settings.corporate_credit_card_expenses_object is not None:
            fund_source.append('CCC')

        create_expense_groups(
            kwargs['workspace_id'],
            fund_source=fund_source,
            task_log=task_log
        )

        return Response(
            status=status.HTTP_200_OK
        )


class ExpenseGroupSettingsView(generics.ListCreateAPIView):
    """
    Expense Group Settings View
    """
    serializer_class = ExpenseGroupSettingsSerializer

    def get(self, request, *args, **kwargs):
        expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=self.kwargs['workspace_id'])

        return Response(
            data=self.serializer_class(expense_group_settings).data,
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        expense_group_settings, _ = ExpenseGroupSettings.update_expense_group_settings(
            request.data, self.kwargs['workspace_id'])
        return Response(
            data=self.serializer_class(expense_group_settings).data,
            status=status.HTTP_200_OK
        )


class ExpenseCustomFieldsView(generics.ListCreateAPIView):
    """
    Project view
    """
    serializer_class = ExpenseAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        attribute_type = self.request.query_params.get('attribute_type')

        return ExpenseAttribute.objects.filter(
            attribute_type=attribute_type, workspace_id=self.kwargs['workspace_id']).order_by('value')

class ExpenseFieldsView(generics.ListAPIView):
    pagination_class = None
    serializer_class = ExpenseFieldSerializer

    def get(self, request, *args, **kwargs):
        default_attributes = ['EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER', 'CORPORATE_CARD', 'TAX_GROUP']
        attributes = ExpenseAttribute.objects.filter(
            ~Q(attribute_type__in=default_attributes),
            workspace_id=self.kwargs['workspace_id']
        ).values('attribute_type', 'display_name').distinct()

        expense_fields= [
            {'attribute_type': 'COST_CENTER', 'display_name': 'Cost Center'},
            {'attribute_type': 'PROJECT', 'display_name': 'Project'}
        ]

        for attribute in attributes:
            expense_fields.append(attribute)

        return Response(
            expense_fields,
            status=status.HTTP_200_OK
        )


class ExpenseGroupScheduleView(generics.CreateAPIView):
    """
    Create expense group schedule
    """

    def post(self, request, *args, **kwargs):
        """
        Post expense schedule
        """
        schedule_expense_group_creation(kwargs['workspace_id'])

        return Response(
            status=status.HTTP_200_OK
        )


class ExpenseGroupSyncView(generics.CreateAPIView):
    """
    Create expense groups
    """
    def post(self, request, *args, **kwargs):
        """
        Post expense groups creation
        """
        task_log, fund_source = get_task_log_and_fund_source(kwargs['workspace_id'])

        async_create_expense_groups(kwargs['workspace_id'], fund_source, task_log)

        return Response(
            status=status.HTTP_200_OK
        )


class ExpenseGroupByIdView(generics.RetrieveAPIView):
    """
    Expense Group by Id view
    """

    def get(self, request, *args, **kwargs):
        """
        Get expenses
        """
        try:
            expense_group = ExpenseGroup.objects.get(
                workspace_id=kwargs['workspace_id'], pk=kwargs['expense_group_id']
            )

            return Response(
                data=ExpenseGroupSerializer(expense_group).data,
                status=status.HTTP_200_OK
            )

        except ExpenseGroup.DoesNotExist:
            return Response(
                data={
                    'message': 'Expense group not found'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ExpenseView(generics.RetrieveAPIView):
    """
    Expense view
    """

    def get(self, request, *args, **kwargs):
        """
        Get expenses
        """
        try:
            expense_group = ExpenseGroup.objects.get(
                workspace_id=kwargs['workspace_id'], pk=kwargs['expense_group_id']
            )
            expenses = Expense.objects.filter(
                id__in=expense_group.expenses.values_list('id', flat=True)).order_by('-updated_at')
            return Response(
                data=ExpenseSerializer(expenses, many=True).data,
                status=status.HTTP_200_OK
            )

        except ExpenseGroup.DoesNotExist:
            return Response(
                data={
                    'message': 'Expense group not found'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeView(generics.ListCreateAPIView):
    """
    Employee view
    """

    serializer_class = ExpenseAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return ExpenseAttribute.objects.filter(
            attribute_type='EMPLOYEE', workspace_id=self.kwargs['workspace_id']).order_by('value')


class CategoryView(generics.ListCreateAPIView):
    """
    Category view
    """

    serializer_class = ExpenseAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return ExpenseAttribute.objects.filter(
            attribute_type='CATEGORY', workspace_id=self.kwargs['workspace_id']).order_by('value')


class CostCenterView(generics.ListCreateAPIView):
    """
    Category view
    """

    serializer_class = ExpenseAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return ExpenseAttribute.objects.filter(
            attribute_type='COST_CENTER', workspace_id=self.kwargs['workspace_id']).order_by('value')


class SyncFyleDimensionView(generics.ListCreateAPIView):
    """
    Sync Fyle Dimensions View
    """

    def post(self, request, *args, **kwargs):
        """
        Sync Data From Fyle
        """
        try:
            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            if workspace.source_synced_at:
                time_interval = datetime.now(timezone.utc) - workspace.source_synced_at

            if workspace.source_synced_at is None or time_interval.days > 0:
                fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

                platform = PlatformConnector(fyle_credentials)
                platform.import_fyle_dimensions()

                workspace.source_synced_at = datetime.now()
                workspace.save(update_fields=['source_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )

        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshFyleDimensionView(generics.ListCreateAPIView):
    """
    Refresh Fyle Dimensions view
    """

    def post(self, request, *args, **kwargs):
        """
        Sync data from Fyle
        """
        try:
            fyle_credentials = FyleCredential.objects.get(workspace_id=kwargs['workspace_id'])

            platform = PlatformConnector(fyle_credentials)
            platform.import_fyle_dimensions()

            workspace = Workspace.objects.get(id=kwargs['workspace_id'])
            workspace.source_synced_at = datetime.now()
            workspace.save(update_fields=['source_synced_at'])

            return Response(
                status=status.HTTP_200_OK
            )
        except FyleCredential.DoesNotExist:
            return Response(
                data={
                    'message': 'Fyle credentials not found in workspace'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ProjectView(generics.ListCreateAPIView):
    """
    Project view
    """
    serializer_class = ExpenseAttributeSerializer
    pagination_class = None

    def get_queryset(self):
        return ExpenseAttribute.objects.filter(
            attribute_type='PROJECT', workspace_id=self.kwargs['workspace_id']).order_by('value')
