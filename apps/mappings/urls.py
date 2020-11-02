from django.urls import path

from .views import TenantMappingView

urlpatterns = [
    path('tenant/', TenantMappingView.as_view()),
]
