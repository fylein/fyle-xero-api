from apps.workspaces.apis.export_settings.triggers import ExportSettingsTrigger
from apps.workspaces.models import WorkspaceGeneralSettings
from apps.tasks.models import TaskLog, Error
from apps.fyle.models import ExpenseGroup


def test_post_save_workspace_general_settings_export_trigger(mocker, db, add_workspace_to_database):
    workspace_id = 100
    workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expenses_object': 'JOURNAL ENTRY',
            'corporate_credit_card_expenses_object': None
        }
    )

    expense_grp_ccc = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True
    ).exclude(fund_source__in=['PERSONAL']).values_list('id', flat=True)

    expense_grp_ccc_count = expense_grp_ccc.count()

    before_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    export_trigger = ExportSettingsTrigger()
    export_trigger.run_workspace_general_settings_triggers(
        workspace_general_settings_instance=workspace_general_settings_instance
    )

    after_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    after_errors_count = Error.objects.filter(
        workspace_id=workspace_id,
        expense_group_id__in=expense_grp_ccc
    ).exclude(type__contains='_MAPPING').count()

    assert after_errors_count == 0
    assert after_delete_count == before_delete_count - expense_grp_ccc_count


def test_post_save_workspace_general_settings_export_trigger_2(mocker, db, add_workspace_to_database):
    workspace_id = 100
    workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expenses_object': 'JOURNAL ENTRY',
            'corporate_credit_card_expenses_object': None
        }
    )

    expense_grp_personal = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True
    ).exclude(fund_source__in=['CCC']).values_list('id', flat=True)

    expense_grp_personal_count = expense_grp_personal.count()

    before_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    export_trigger = ExportSettingsTrigger()
    export_trigger.run_workspace_general_settings_triggers(
        workspace_general_settings_instance=workspace_general_settings_instance
    )

    after_delete_count = TaskLog.objects.filter(
        workspace_id=workspace_id,
        status__in=['FAILED', 'FATAL']
    ).count()

    after_errors_count = Error.objects.filter(
        workspace_id=workspace_id,
        expense_group_id__in=expense_grp_personal
    ).exclude(type__contains='_MAPPING').count()

    assert after_errors_count == 0
    assert after_delete_count == before_delete_count - expense_grp_personal_count
