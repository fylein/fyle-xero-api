from rest_framework import generics, status
from rest_framework.response import Response

from apps.workspaces.models import Workspace

from .helpers import get_latest_workspace_id
from .serializers import PrefillConfigurationsSerializer


class PrefillConfigurationsView(generics.RetrieveUpdateAPIView):
    serializer_class = PrefillConfigurationsSerializer

    def get_object(self):
        latest_workspace_id = get_latest_workspace_id(self.request.user)

        return Workspace.objects.filter(id=latest_workspace_id).first()

class PrefillConfigurationsAvailabilityView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        latest_workspace_id = get_latest_workspace_id(self.request.user)

        return Response(
            data={
                'is_available': True if latest_workspace_id else False
            },
            status=status.HTTP_200_OK
        )
