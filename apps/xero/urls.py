from django.urls import path

from .views import TenantView, AccountView, BankAccountView, TrackingCategoryView, ContactView, \
    ItemView, XeroFieldsView, BankTransactionView, BankTransactionScheduleView, BillView, BillScheduleView, \
    OrganisationView, PaymentView, ReimburseXeroPaymentsView, SyncXeroDimensionView, RefreshXeroDimensionView

urlpatterns = [
    path('accounts/', AccountView.as_view()),
    path('bank_accounts/', BankAccountView.as_view()),
    path('tracking_categories/', TrackingCategoryView.as_view()),
    path('contacts/', ContactView.as_view()),
    path('items/', ItemView.as_view()),
    path('tenants/', TenantView.as_view()),
    path('xero_fields/', XeroFieldsView.as_view()),
    path('bank_transactions/', BankTransactionView.as_view()),
    path('bank_transactions/trigger/', BankTransactionScheduleView.as_view()),
    path('bills/', BillView.as_view()),
    path('bills/trigger/', BillScheduleView.as_view()),
    path('organisations/', OrganisationView.as_view()),
    path('payments/', PaymentView.as_view()),
    path('reimburse_payments/', ReimburseXeroPaymentsView.as_view()),
    path('sync_dimensions/', SyncXeroDimensionView.as_view()),
    path('refresh_dimensions/', RefreshXeroDimensionView.as_view())
]
