from django.urls import path

from .views import FyleOrgsView

from apps.workspaces.apis.clone_settings.views \
    import CloneSettingsExistsView

urlpatterns = [
    path('orgs/', FyleOrgsView.as_view()),
    path(
        'clone_settings/exists/',
        CloneSettingsExistsView.as_view()
    ),
]
    