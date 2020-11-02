from django.urls import path, include

from .views import TenantMappingView, GeneralMappingView

urlpatterns = [
    path('tenant/', TenantMappingView.as_view()),
    path('general/', GeneralMappingView.as_view()),
    path('', include('fyle_accounting_mappings.urls'))
]
