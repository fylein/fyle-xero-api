from rest_framework import generics

from apps.workspaces.models import Workspace

from .helpers import get_latest_workspace_id
from .serializers import PrefillConfigurationsSerializer


class PrefillConfigurationsView(generics.RetrieveUpdateAPIView):
    serializer_class = PrefillConfigurationsSerializer

    def get_object(self):
        latest_workspace_id = get_latest_workspace_id(self.request.user)

        return Workspace.objects.filter(id=latest_workspace_id).first()
