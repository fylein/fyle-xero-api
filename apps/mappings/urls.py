from django.urls import path

from .views import TenantMappingView, GeneralMappingView

urlpatterns = [
    path('tenant/', TenantMappingView.as_view()),
    path('general/', GeneralMappingView.as_view())
]
