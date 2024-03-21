"""fyle_accounting_mappings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import (
    CategoryAttributesMappingView,
    MappingSettingsView,
    MappingsView,
    EmployeeMappingsView,
    CategoryMappingsView,
    SearchDestinationAttributesView,
    MappingStatsView,
    ExpenseAttributesMappingView,
    EmployeeAttributesMappingView,
    ExpenseFieldView,
    DestinationAttributesView,
    FyleFieldsView,
    PaginatedDestinationAttributesView
)

urlpatterns = [
    path('settings/', MappingSettingsView.as_view()),
    path('settings/<int:pk>/', MappingSettingsView.as_view()),
    path('employee/', EmployeeMappingsView.as_view()),
    path('category/', CategoryMappingsView.as_view()),
    path('destination_attributes/search/', SearchDestinationAttributesView.as_view()),
    path('stats/', MappingStatsView.as_view()),
    path('', MappingsView.as_view()),
    path('expense_attributes/', ExpenseAttributesMappingView.as_view()),
    path('category_attributes/', CategoryAttributesMappingView.as_view()),
    path('employee_attributes/', EmployeeAttributesMappingView.as_view()),
    path('expense_fields/', ExpenseFieldView.as_view()),
    path('destination_attributes/', DestinationAttributesView.as_view()),
    path('fyle_fields/', FyleFieldsView.as_view()),
    path('paginated_destination_attributes/', PaginatedDestinationAttributesView.as_view()),
]
