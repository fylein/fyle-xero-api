from django.db.models import Q

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status

from fyle_xero_api.utils import assert_valid

from .models import TaskLog
from .serializers import TaskLogSerializer
from fyle_xero_api.utils import LookupFieldMixin


class TasksView(LookupFieldMixin,generics.ListAPIView):
    """
    Tasks view
    """
    serializer_class = TaskLogSerializer
    queryset = TaskLog.objects.all()
    filterset_fields = {'type':{'exact', 'in'}, 'expense_group_id':{'exact', 'in'}, 'status':{'exact', 'in'}}
    ordering_fields = ('updated_at',)
