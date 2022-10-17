from django.urls import path

from .views import ExpenseGroupView, ExpenseGroupByIdView, ExpenseGroupScheduleView, ExpenseView, EmployeeView, \
    CategoryView, CostCenterView, ProjectView, ExpenseFieldsView, ExpenseCustomFieldsView, \
    ExpenseGroupSettingsView, SyncFyleDimensionView, RefreshFyleDimensionView, ExpenseGroupSyncView

urlpatterns = [
    path('expense_groups/', ExpenseGroupView.as_view()),
    path('expense_groups/trigger/', ExpenseGroupScheduleView.as_view()),
    path('expense_groups/sync/', ExpenseGroupSyncView.as_view(), name='sync-expense-groups'),
    path('expense_groups/<int:expense_group_id>/', ExpenseGroupByIdView.as_view()),
    path('expense_groups/<int:expense_group_id>/expenses/', ExpenseView.as_view()),
    path('employees/', EmployeeView.as_view()),
    path('categories/', CategoryView.as_view()),
    path('cost_centers/', CostCenterView.as_view()),
    path('projects/', ProjectView.as_view()),
    path('expense_custom_fields/', ExpenseCustomFieldsView.as_view()),
    path('expense_fields/', ExpenseFieldsView.as_view()),
    path('expense_group_settings/', ExpenseGroupSettingsView.as_view()),
    path('sync_dimensions/', SyncFyleDimensionView.as_view()),
    path('refresh_dimensions/', RefreshFyleDimensionView.as_view())
]
