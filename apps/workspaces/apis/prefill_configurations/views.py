from rest_framework import generics

from apps.workspaces.models import Workspace

from .serializers import PrefillConfigurationsSerializer


class PrefillConfigurationsView(generics.RetrieveUpdateAPIView):
    serializer_class = PrefillConfigurationsSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs['workspace_id']).first()
