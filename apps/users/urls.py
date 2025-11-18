from django.urls import path

from apps.workspaces.apis.clone_settings.views import CloneSettingsExistsView

urlpatterns = [
    path("clone_settings/exists/", CloneSettingsExistsView.as_view()),
]
