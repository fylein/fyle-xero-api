from django.urls import path, include

from .views import WorkspaceAdminsView, WorkspaceView, ReadyView, ConnectXeroView, GeneralSettingsView, \
    RevokeXeroConnectionView, XeroExternalSignUpsView, ExportToXeroView, LastExportDetailView

urlpatterns = [
    path('', WorkspaceView.as_view()),
    path('ready/', ReadyView.as_view()),
    path('<int:workspace_id>/', WorkspaceView.as_view()),
    path('<int:workspace_id>/connect_xero/authorization_code/', ConnectXeroView.as_view()),
    path('<int:workspace_id>/credentials/xero/', ConnectXeroView.as_view()),
    path('<int:workspace_id>/connection/xero/revoke/', RevokeXeroConnectionView.as_view()),
    path('<int:workspace_id>/exports/trigger/', ExportToXeroView.as_view(), name='export-to-xero'),
    path('<int:workspace_id>/settings/general/', GeneralSettingsView.as_view()),
    path('<int:workspace_id>/fyle/', include('apps.fyle.urls')),
    path('<int:workspace_id>/tasks/', include('apps.tasks.urls')),
    path('<int:workspace_id>/xero/', include('apps.xero.urls')),
    path('<int:workspace_id>/mappings/', include('apps.mappings.urls')),
    path('<int:workspace_id>/admins/', WorkspaceAdminsView.as_view(), name='admin'),
    path('external_signup/', XeroExternalSignUpsView.as_view()),
    path('<int:workspace_id>/export_detail/', LastExportDetailView.as_view(), name='export-detail'),
]
