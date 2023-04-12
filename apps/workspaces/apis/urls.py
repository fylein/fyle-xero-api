from django.urls import path

from .export_settings.views import ExportSettingsView
from .import_settings.views import ImportSettingsView
from .advanced_settings.views import AdvancedSettingsView
from .clone_settings.views import CloneSettingsView
from .errors.views import ErrorsView

urlpatterns = [
    path('<int:workspace_id>/export_settings/', ExportSettingsView.as_view()),
    path('<int:workspace_id>/import_settings/', ImportSettingsView.as_view()),
    path('<int:workspace_id>/advanced_settings/', AdvancedSettingsView.as_view()),
    path('<int:workspace_id>/clone_settings/', CloneSettingsView.as_view()),
    path('<int:workspace_id>/errors/', ErrorsView.as_view())
]
