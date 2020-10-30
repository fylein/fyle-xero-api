from django.urls import path, include

from .views import WorkspaceView, ReadyView, ConnectFyleView, ConnectXeroView, GeneralSettingsView

urlpatterns = [
    path('', WorkspaceView.as_view({'get': 'get', 'post': 'post'})),
    path('ready/', ReadyView.as_view({'get': 'get'})),
    path('<int:workspace_id>/', WorkspaceView.as_view({'get': 'get_by_id'})),
    path('<int:workspace_id>/connect_fyle/authorization_code/', ConnectFyleView.as_view({'post': 'post'})),
    path('<int:workspace_id>/credentials/fyle/', ConnectFyleView.as_view({'get': 'get'})),
    path('<int:workspace_id>/credentials/fyle/delete/', ConnectFyleView.as_view({'post': 'delete'})),
    path('<int:workspace_id>/connect_xero/authorization_code/', ConnectXeroView.as_view({'post': 'post'})),
    path('<int:workspace_id>/credentials/xero/', ConnectXeroView.as_view({'get': 'get'})),
    path('<int:workspace_id>/credentials/xero/delete/', ConnectXeroView.as_view({'post': 'delete'})),
    path('<int:workspace_id>/settings/general/', GeneralSettingsView.as_view({'post': 'post', 'get': 'get'})),
    path('<int:workspace_id>/fyle/', include('apps.fyle.urls')),
    path('<int:workspace_id>/tasks/', include('apps.tasks.urls')),
]

# Add Xero and Mapping URL's once finished
