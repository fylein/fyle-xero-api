from rest_framework import generics

from apps.tasks.models import TaskLog
from apps.tasks.serializers import TaskLogSerializer
from fyle_xero_api.utils import LookupFieldMixin


class TasksView(LookupFieldMixin, generics.ListAPIView):
    """
    Tasks view
    """

    serializer_class = TaskLogSerializer
    queryset = TaskLog.objects.all()
    filterset_fields = {
        "type": {"exact", "in"},
        "expense_group_id": {"exact", "in"},
        "status": {"exact", "in"},
    }
    ordering_fields = ("updated_at",)
