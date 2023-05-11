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

    def put(self, request, **kwargs):
        workspace_instance = Workspace.objects.get(id=kwargs['workspace_id'])
        serializer = CloneSettingsSerializer(workspace_instance, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )


class CloneSettingsExistsView(generics.RetrieveAPIView):

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
