from django.db.models import Q

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_xero_api.utils import assert_valid

from .models import TaskLog
from .serializers import TaskLogSerializer


class TasksView(generics.ListAPIView):
    """
    Tasks view
    """
    serializer_class = TaskLogSerializer

    def get_queryset(self):
        """
        Return task logs in workspace
        """
        task_type = self.request.query_params.get('task_type')
        expense_group_ids = self.request.query_params.get('expense_group_ids')
        task_status = self.request.query_params.get('status')

        filters = {
            'workspace_id': self.kwargs['workspace_id']
        }

        if task_type:
            filters['type__in'] = task_type.split(',')

        if expense_group_ids:
            filters['expense_group_id__in'] = expense_group_ids.split(',')

        if task_status:
            filters['status__in'] = task_status.split(',')

        return TaskLog.objects.filter(**filters).order_by('-updated_at').all()
    