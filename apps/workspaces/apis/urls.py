from django.urls import path

from apps.workspaces.apis.advanced_settings.views import AdvancedSettingsView
from apps.workspaces.apis.clone_settings.views import CloneSettingsView
from apps.workspaces.apis.errors.views import ErrorsView
from apps.workspaces.apis.export_settings.views import ExportSettingsView
from apps.workspaces.apis.import_settings.views import ImportSettingsView

urlpatterns = [
    path("<int:workspace_id>/export_settings/", ExportSettingsView.as_view()),
    path("<int:workspace_id>/import_settings/", ImportSettingsView.as_view()),
    path("<int:workspace_id>/advanced_settings/", AdvancedSettingsView.as_view()),
    path("<int:workspace_id>/clone_settings/", CloneSettingsView.as_view()),
    path("<int:workspace_id>/errors/", ErrorsView.as_view()),
]
