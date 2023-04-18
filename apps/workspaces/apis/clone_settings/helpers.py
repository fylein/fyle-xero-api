from django.contrib.auth import get_user_model
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings

User = get_user_model()


def get_latest_workspace(user_id: str):
    """
    Get latest workspace for user

    :param user_id: user id
    :return: workspace id / None
    """
    user = User.objects.get(user_id=user_id)
    user_workspaces = Workspace.objects.filter(user__in=[user]).values_list('id', flat=True)

    workspace_general_setting = WorkspaceGeneralSettings.objects.filter(
        workspace_id__in=user_workspaces,
        workspace__onboarding_state='COMPLETE'
    ).order_by('-updated_at').first()

    if workspace_general_setting:
        return workspace_general_setting.workspace
