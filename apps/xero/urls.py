from django.urls import path

from apps.xero.views import (
    DestinationAttributesView,
    RefreshXeroDimensionView,
    SyncXeroDimensionView,
    TenantView,
    TokenHealthView,
    XeroFieldsView,
)

urlpatterns = [
    path("tenants/", TenantView.as_view()),
    path("xero_fields/", XeroFieldsView.as_view()),
    path("token_health/", TokenHealthView.as_view()),
    path("sync_dimensions/", SyncXeroDimensionView.as_view()),
    path("refresh_dimensions/", RefreshXeroDimensionView.as_view()),
    path("destination_attributes/", DestinationAttributesView.as_view()),
]
