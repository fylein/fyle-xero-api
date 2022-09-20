from django.urls import path

from .export_settings.views import ExportSettingsView

urlpatterns = [
    path('<int:workspace_id>/export_settings/', ExportSettingsView.as_view()),
]
