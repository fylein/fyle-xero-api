from rest_framework import generics

from apps.tasks.models import Error

from .serializers import ErrorSerializer


class ErrorsView(generics.ListAPIView):
    serializer_class = ErrorSerializer
    pagination_class = None
    
    def get_queryset(self):
        type = self.request.query_params.get('type')
        
        is_resolved = self.request.query_params.get('is_resolved', None)

        params = {
            'workspace__id': self.kwargs.get('workspace_id')
        }

        if is_resolved and is_resolved.lower() == 'true':
            is_resolved = True
        elif is_resolved and is_resolved.lower() == 'false':
            is_resolved = False

        if is_resolved is not None:
            params['is_resolved'] = is_resolved

        if type:
            params['type'] = type

        return Error.objects.filter(**params)
