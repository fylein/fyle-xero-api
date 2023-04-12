from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.workspaces.models import Workspace

from .helpers import get_latest_workspace
from .serializers import CloneSettingsSerializer


class CloneSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = CloneSettingsSerializer

    def get_object(self):
        latest_workspace = get_latest_workspace(self.request.user)

        return Workspace.objects.filter(id=latest_workspace.id).first()

class CloneSettingsAvailabilityView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        latest_workspace = get_latest_workspace(self.request.user)

        return Response(
            data={
                'is_available': True if latest_workspace else False,
                'workspace_name': latest_workspace.name if latest_workspace else None
            },
            status=status.HTTP_200_OK
        )
