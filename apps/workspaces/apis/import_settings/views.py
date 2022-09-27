from rest_framework import generics

from apps.workspaces.models import Workspace

from .serializers import ImportSettingsSerializer


class ImportSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ImportSettingsSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs['workspace_id']).first()
