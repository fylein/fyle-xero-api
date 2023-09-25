from django.urls import include, path

from apps.mappings.views import AutoMapEmployeeView, TenantMappingView

urlpatterns = [
    path("tenant/", TenantMappingView.as_view()),
    path("", include("fyle_accounting_mappings.urls")),
    path("auto_map_employees/trigger/", AutoMapEmployeeView.as_view()),
]
