from rest_framework import generics

from apps.workspaces.models import Workspace

from .serializers import ExportSettingsSerializer

class ExportSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ExportSettingsSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs['workspace_id']).first()