from django.urls import path

from .views import TenantView, AccountView, BankAccountView, TrackingCategoryView, ContactView

urlpatterns = [
    path('accounts/', AccountView.as_view()),
    path('bank_accounts/', BankAccountView.as_view()),
    path('tracking_categories/', TrackingCategoryView.as_view()),
    path('contacts/', ContactView.as_view()),
    path('tenants/', TenantView.as_view()),
]
