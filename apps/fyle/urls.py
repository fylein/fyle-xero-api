from django.urls import path

from apps.fyle.views import (
    ExpenseFieldsView,
    ExpenseGroupSettingsView,
    ExpenseGroupSyncView,
    ExpenseGroupView,
    ExportableExpenseGroupsView,
    RefreshFyleDimensionView,
    SyncFyleDimensionView,
)

urlpatterns = [
    path("expense_groups/", ExpenseGroupView.as_view()),
    path(
        "exportable_expense_groups/",
        ExportableExpenseGroupsView.as_view(),
        name="exportable-expense-groups",
    ),
    path(
        "expense_groups/sync/",
        ExpenseGroupSyncView.as_view(),
        name="sync-expense-groups",
    ),
    path("expense_fields/", ExpenseFieldsView.as_view()),
    path("expense_group_settings/", ExpenseGroupSettingsView.as_view()),
    path("sync_dimensions/", SyncFyleDimensionView.as_view()),
    path("refresh_dimensions/", RefreshFyleDimensionView.as_view()),
]
