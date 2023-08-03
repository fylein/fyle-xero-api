from django.urls import path, include

from .views import TenantMappingView, AutoMapEmployeeView

urlpatterns = [
    path('tenant/', TenantMappingView.as_view()),
    path('', include('fyle_accounting_mappings.urls')),
    path('auto_map_employees/trigger/', AutoMapEmployeeView.as_view())
]
