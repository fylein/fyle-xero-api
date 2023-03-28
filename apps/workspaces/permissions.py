from django.contrib.auth import get_user_model
from rest_framework import permissions
from django.core.cache import cache

from apps.workspaces.models import Workspace

from cryptography.fernet import Fernet

from django.conf import settings

User = get_user_model()


class WorkspacePermissions(permissions.BasePermission):
    """
    Permission check for users <> workspaces
    """

    def validate_and_cache(self, workspace_users, user: User, workspace_id: str, cache_users: bool = False):
        if user.id in workspace_users:
            if cache_users:
                cache.set(workspace_id, workspace_users, 172800)
            return True

        return False

    def has_permission(self, request, view):
        workspace_id = str(view.kwargs.get('workspace_id'))
        user = request.user
        workspace_users = cache.get(workspace_id)

        if workspace_users:
            return self.validate_and_cache(workspace_users, user, workspace_id)
        else:
            workspace_users = Workspace.objects.filter(pk=workspace_id).values_list('user', flat=True)
            return self.validate_and_cache(workspace_users, user, workspace_id, True)


class IsAuthenticatedForTest(permissions.BasePermission):
    """
    Custom auth for preparing a workspace for e2e tests
    """
    def has_permission(self, request, view):
        # Client sends a token in the header, which we decrypt and compare with the Client Secret
        cipher_suite = Fernet(settings.ENCRYPTION_KEY)
        try:
            decrypted_password = cipher_suite.decrypt(request.headers['X-E2E-Tests-Client-ID'].encode('utf-8')).decode('utf-8')
            if decrypted_password == settings.E2E_TESTS_CLIENT_SECRET:
                return True
        except:
            return False

        return False
