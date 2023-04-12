from django.urls import path

from .views import UserProfileView, FyleOrgsView

from apps.workspaces.apis.clone_settings.views \
    import CloneSettingsAvailabilityView

urlpatterns = [
    path('profile/', UserProfileView.as_view()),
    path('orgs/', FyleOrgsView.as_view()),
    path(
        'clone_settings/availability/',
        CloneSettingsAvailabilityView.as_view()
    ),
]
