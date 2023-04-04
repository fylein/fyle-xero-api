from django.contrib.auth import get_user_model
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings

User = get_user_model()

def get_latest_workspace_id(user_id: str) -> int:
    """
    Get latest workspace id for user

    :param user_id: user id
    :return: workspace id
    """
    user = User.objects.get(user_id=user_id)
    user_workspaces = Workspace.objects.filter(user__in=[user]).values_list('id', flat=True)

    # TODO: handle case when user has no COMPLETE workspaces
    return WorkspaceGeneralSettings.objects.filter(
        workspace_id__in=user_workspaces,
        workspace__onboarding_state='COMPLETE'
    ).order_by('-updated_at').first().workspace.id
