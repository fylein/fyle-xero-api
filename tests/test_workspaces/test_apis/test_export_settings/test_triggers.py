from datetime import datetime, timezone

from apps.fyle.models import ExpenseGroup
from apps.tasks.models import Error, TaskLog
from apps.workspaces.apis.export_settings.triggers import ExportSettingsTrigger
from apps.workspaces.models import LastExportDetail, WorkspaceGeneralSettings


def test_post_save_workspace_general_settings_export_trigger(mocker, db, add_workspace_to_database):
    workspace_id = 1
    LastExportDetail.objects.update_or_create(workspace_id=workspace_id, defaults={'last_exported_at': datetime.now(timezone.utc)})
    workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expenses_object': 'JOURNAL ENTRY',
            'corporate_credit_card_expenses_object': None
        }
    )

    ExpenseGroup.objects.filter(workspace_id=workspace_id).exclude(
        fund_source__in=['PERSONAL']
    ).update(exported_at=None)

    expense_grp_ccc = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True
    ).exclude(fund_source__in=['PERSONAL']).values_list('id', flat=True)

    old_configurations = {
        'reimbursable_expenses_object': 'BILL',
        'corporate_credit_card_expenses_object': None
    }

    export_trigger = ExportSettingsTrigger()
    export_trigger.run_workspace_general_settings_triggers(
        workspace_general_settings_instance,
        old_configurations
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
    assert after_delete_count == 0


def test_post_save_workspace_general_settings_export_trigger_2(mocker, db, add_workspace_to_database):
    workspace_id = 1
    LastExportDetail.objects.update_or_create(workspace_id=workspace_id, defaults={'last_exported_at': datetime.now(timezone.utc)})
    workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expenses_object': None,
            'corporate_credit_card_expenses_object': 'JOURNAL ENTRY'
        }
    )

    ExpenseGroup.objects.filter(workspace_id=workspace_id).exclude(
        fund_source__in=['CCC']
    ).update(exported_at=None)

    expense_grp_personal = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True
    ).exclude(fund_source__in=['CCC']).values_list('id', flat=True)

    old_configurations = {
        'reimbursable_expenses_object': None,
        'corporate_credit_card_expenses_object': 'BANK TRANSACTION'
    }

    export_trigger = ExportSettingsTrigger()
    export_trigger.run_workspace_general_settings_triggers(
        workspace_general_settings_instance,
        old_configurations
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
    assert after_delete_count == 0
