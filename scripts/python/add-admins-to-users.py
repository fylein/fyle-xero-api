from fyle_integrations_platform_connector import PlatformConnector
from django.db.models import Q

from apps.workspaces.models import FyleCredential, Workspace
from apps.users.models import User

workspaces = Workspace.objects.filter(
    ~Q(name__icontains='fyle for') & ~Q(name__icontains='test')
)

for workspace in workspaces:
    try:
        workspace_id = workspace.id
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)
        users = []
        admins = platform.employees.get_admins()
        existing_user_ids = User.objects.filter(workspace__id=workspace_id).values_list('user_id', flat=True)
        for admin in admins:
            # Skip already existing users
            if admin['user_id'] not in existing_user_ids:
                users.append(User(email=admin['email'], user_id=admin['user_id'], full_name=admin['full_name']))
        if len(users):
            created_users = User.objects.bulk_create(users, batch_size=50)
            workspace = Workspace.objects.get(id=workspace_id)
            for user in created_users:
                workspace.user.add(user)
    except Exception as e:
        print(e.__dict__)
