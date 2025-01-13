from rest_framework import generics

from apps.workspaces.apis.advanced_settings.serializers import AdvancedSettingsSerializer
from apps.workspaces.models import Workspace


class AdvancedSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = AdvancedSettingsSerializer

    def get_object(self):
        return Workspace.objects.filter(id=self.kwargs["workspace_id"]).first()

    def get_serializer_context(self):
        """
        Override to include the request in the serializer context.
        This allows serializers to access the current user.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
