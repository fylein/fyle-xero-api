import hashlib
import logging
import traceback
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from django.db import transaction
from django.db.models import Count, Q
from django.utils.module_loading import import_string
from fyle.platform.exceptions import InternalServerError
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle.platform.exceptions import RetryException
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_library.fyle_platform.helpers import filter_expenses_based_on_state, get_expense_import_states
from fyle_accounting_mappings.models import ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector
from fyle_integrations_platform_connector.apis.expenses import Expenses as FyleExpenses

from apps.fyle.actions import mark_expenses_as_skipped, post_accounting_export_summary
from apps.fyle.enums import ExpenseStateEnum, FundSourceEnum, PlatformExpensesEnum
from apps.fyle.helpers import get_fund_source, get_source_account_type, handle_import_exception, update_task_log_post_import
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import Error, TaskLog
from apps.workspaces.actions import export_to_xero
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings, WorkspaceSchedule

logger = logging.getLogger(__name__)
logger.level = logging.INFO


SOURCE_ACCOUNT_MAP = {
    FundSourceEnum.PERSONAL: PlatformExpensesEnum.PERSONAL_CASH_ACCOUNT,
    FundSourceEnum.CCC: PlatformExpensesEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT
}

# Reverse mapping for fund source change detection
REVERSE_SOURCE_ACCOUNT_MAP = {
    PlatformExpensesEnum.PERSONAL_CASH_ACCOUNT: FundSourceEnum.PERSONAL,
    PlatformExpensesEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT: FundSourceEnum.CCC
}


def get_task_log_and_fund_source(workspace_id: int):
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type=TaskLogTypeEnum.FETCHING_EXPENSES,
        defaults={"status": TaskLogStatusEnum.IN_PROGRESS},
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append(FundSourceEnum.PERSONAL)
    if general_settings.corporate_credit_card_expenses_object is not None:
        fund_source.append(FundSourceEnum.CCC)

    return task_log, fund_source


def create_expense_groups(
    workspace_id: int, fund_source: List[str], task_log: TaskLog | None, imported_from: ExpenseImportSourceEnum
):
    try:
        with transaction.atomic():
            expense_group_settings = ExpenseGroupSettings.objects.get(
                workspace_id=workspace_id
            )
            workspace = Workspace.objects.get(pk=workspace_id)
            last_synced_at = workspace.last_synced_at if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE else None
            ccc_last_synced_at = workspace.ccc_last_synced_at if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE else None
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            platform = PlatformConnector(fyle_credentials)

            expenses = []
            reimbursable_expenses_count = 0

            if last_synced_at:
                last_synced_at = last_synced_at - timedelta(minutes=5)

            if FundSourceEnum.PERSONAL in fund_source:
                source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL]]

                expenses.extend(
                    platform.expenses.get(
                        source_account_type=source_account_type,
                        state=expense_group_settings.reimbursable_expense_state,
                        settled_at=last_synced_at
                        if expense_group_settings.reimbursable_expense_state
                        == ExpenseStateEnum.PAYMENT_PROCESSING
                        else None,
                        filter_credit_expenses=False,
                        last_paid_at=last_synced_at
                        if expense_group_settings.reimbursable_expense_state == ExpenseStateEnum.PAID
                        else None,
                    )
                )

            if workspace.last_synced_at or expenses:
                workspace.last_synced_at = datetime.now()
                reimbursable_expenses_count += len(expenses)

            if ccc_last_synced_at:
                ccc_last_synced_at = ccc_last_synced_at - timedelta(minutes=5)

            if FundSourceEnum.CCC in fund_source:
                source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.CCC]]

                expenses.extend(
                    platform.expenses.get(
                        source_account_type=source_account_type,
                        state=expense_group_settings.ccc_expense_state,
                        settled_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state
                        == ExpenseStateEnum.PAYMENT_PROCESSING
                        else None,
                        approved_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state == ExpenseStateEnum.APPROVED
                        else None,
                        filter_credit_expenses=False,
                        last_paid_at=ccc_last_synced_at
                        if expense_group_settings.ccc_expense_state == ExpenseStateEnum.PAID
                        else None,
                    )
                )

            if workspace.ccc_last_synced_at or len(expenses) != reimbursable_expenses_count:
                workspace.ccc_last_synced_at = datetime.now()

            if imported_from != ExpenseImportSourceEnum.CONFIGURATION_UPDATE:
                workspace.save()

            group_expenses_and_save(expenses, task_log, workspace, imported_from=imported_from)

    except FyleCredential.DoesNotExist:
        logger.info("Fyle credentials not found %s", workspace_id)
        update_task_log_post_import(
            task_log,
            TaskLogStatusEnum.FAILED,
            "Fyle credentials do not exist in workspace"
        )

    except FyleInvalidTokenError:
        logger.info("Invalid Token for Fyle")
        update_task_log_post_import(
            task_log,
            TaskLogStatusEnum.FAILED,
            "Invalid Fyle credentials"
        )

    except (RetryException, InternalServerError) as e:
        error_msg = f"Fyle {e.__class__.__name__} occurred"
        logger.info("%s in workspace_id: %s", error_msg, workspace_id)
        update_task_log_post_import(
            task_log,
            TaskLogStatusEnum.FATAL if isinstance(e, RetryException) else TaskLogStatusEnum.FAILED,
            error_msg
        )

    except Exception:
        error = traceback.format_exc()
        logger.exception(
            "Something unexpected happened workspace_id: %s",
            workspace_id
        )
        update_task_log_post_import(task_log, TaskLogStatusEnum.FATAL, error=error)


def check_interval_and_sync_dimension(workspace_id: int):
    """
    Check sync interval and sync dimension
    :param workspace_id: Workspace ID
    """
    workspace = Workspace.objects.get(id=workspace_id)

    time_interval = None
    if workspace.source_synced_at:
        time_interval = datetime.now(timezone.utc) - workspace.source_synced_at

    if workspace.source_synced_at is None or time_interval.days > 0:
        sync_dimensions(workspace_id)


def sync_dimensions(workspace_id: int, is_export: bool = False):
    """
    Sync dimensions
    :param workspace_id: workspace id
    :param is_export: is export
    :return: None
    """
    workspace = Workspace.objects.get(id=workspace_id)
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentials)
    platform.import_fyle_dimensions(is_export=is_export)

    unmapped_card_count = ExpenseAttribute.objects.filter(
        attribute_type="CORPORATE_CARD", workspace_id=workspace_id, active=True, mapping__isnull=True
    ).count()
    if workspace_general_settings and workspace_general_settings.corporate_credit_card_expenses_object:
        import_string('apps.workspaces.helpers.patch_integration_settings_for_unmapped_cards')(workspace_id=workspace_id, unmapped_card_count=unmapped_card_count)

    if is_export:
        categories_count = platform.categories.get_count()

        categories_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="CATEGORY", workspace_id=fyle_credentials.workspace_id, active=True
        ).count()

        if categories_count != categories_expense_attribute_count:
            platform.categories.sync()

        projects_count = platform.projects.get_count()

        projects_expense_attribute_count = ExpenseAttribute.objects.filter(
            attribute_type="PROJECT", workspace_id=fyle_credentials.workspace_id, active=True
        ).count()

        if projects_count != projects_expense_attribute_count:
            platform.projects.sync()

    workspace.source_synced_at = datetime.now()
    workspace.save(update_fields=["source_synced_at"])


def skip_expenses_and_post_accounting_export_summary(expense_ids: List[int], workspace: Workspace):
    """
    Skip expenses and post accounting export summary
    :param expense_ids: List of expense ids
    :param workspace: Workspace
    :return: None
    """
    skipped_expenses = mark_expenses_as_skipped(Q(), expense_ids, workspace)
    if skipped_expenses:
        try:
            post_accounting_export_summary(workspace_id=workspace.id, expense_ids=[expense.id for expense in skipped_expenses])
        except Exception:
            logger.exception('Error posting accounting export summary for workspace_id: %s', workspace.id)


def group_expenses_and_save(
    expenses: List[Dict],
    task_log: TaskLog,
    workspace: Workspace,
    imported_from: ExpenseImportSourceEnum = None,
):
    """
    Group expenses and save
    :param expenses: expenses
    :param task_log: task log
    :param workspace: workspace
    :param imported_from: imported from
    """
    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace.id)
    expense_objects = Expense.create_expense_objects(expenses, workspace.id, imported_from=imported_from)
    filtered_expenses = expense_objects
    expenses_object_ids = [expense_object.id for expense_object in expense_objects]

    filtered_expenses = Expense.objects.filter(
        id__in=expenses_object_ids,
        expensegroup__isnull=True,
        org_id=workspace.fyle_org_id
    )

    # remove negative expenses if fund_source is PERSONAL
    negative_expense_ids = [e.id for e in expense_objects if e.amount < 0 and e.fund_source == FundSourceEnum.PERSONAL]
    if negative_expense_ids:
        expense_objects = [e for e in expense_objects if e.id not in negative_expense_ids]
        skip_expenses_and_post_accounting_export_summary(negative_expense_ids, workspace)

    # Skip reimbursable expenses if reimbursable expense settings is not configured
    if not configuration.reimbursable_expenses_object:
        reimbursable_expense_ids = [e.id for e in expense_objects if e.fund_source == FundSourceEnum.PERSONAL]

        if reimbursable_expense_ids:
            expense_objects = [e for e in expense_objects if e.id not in reimbursable_expense_ids]
            skip_expenses_and_post_accounting_export_summary(reimbursable_expense_ids, workspace)

    # Skip corporate credit card expenses if corporate credit card expense settings is not configured
    if not configuration.corporate_credit_card_expenses_object:
        ccc_expense_ids = [e.id for e in expense_objects if e.fund_source == FundSourceEnum.CCC]

        if ccc_expense_ids:
            expense_objects = [e for e in expense_objects if e.id not in ccc_expense_ids]
            skip_expenses_and_post_accounting_export_summary(ccc_expense_ids, workspace)

    filtered_expenses = expense_objects

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        filtered_expenses, workspace.id
    )

    task_log.status = 'COMPLETE'
    task_log.save()


def import_and_export_expenses(report_id: str, org_id: str, is_state_change_event: bool, report_state: str = None, imported_from: ExpenseImportSourceEnum = None) -> None:
    """
    Import and export expenses
    :param report_id: report id
    :param org_id: org id
    :return: None
    """
    task_log = None
    workspace = Workspace.objects.get(fyle_org_id=org_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace.id)

    import_states = get_expense_import_states(expense_group_settings)

    # Don't call API if report state is not in import states, for example customer configured to import only PAID reports but webhook is triggered for APPROVED report (this is only for is_state_change_event webhook calls)
    if is_state_change_event and report_state and report_state not in import_states:
        return

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)
    task_log = None

    try:
        with transaction.atomic():
            fund_source = get_fund_source(workspace.id)

            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

            if imported_from == ExpenseImportSourceEnum.DIRECT_EXPORT:
                source_account_type = [SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL], SOURCE_ACCOUNT_MAP[FundSourceEnum.CCC]]
            else:
                # We would hit this else block for webhook calls.
                source_account_type = get_source_account_type(fund_source)

            platform = PlatformConnector(fyle_credentials)
            expenses = platform.expenses.get(
                source_account_type,
                filter_credit_expenses=False,
                report_id=report_id,
                import_states=import_states if is_state_change_event else None
            )

            if is_state_change_event:
                expenses = filter_expenses_based_on_state(expenses, expense_group_settings)

            # Check for fund source changes if expenses exist for this report and report state is approved
            existing_expenses = Expense.objects.filter(workspace_id=workspace.id, report_id=report_id).exists()
            if existing_expenses and expenses and expenses[0].get('state') in ['APPROVED', 'ADMIN_APPROVED']:
                handle_expense_fund_source_change(workspace.id, report_id, platform)

            group_expenses_and_save(expenses, task_log, workspace, imported_from=imported_from)

        # Export only selected expense groups
        expense_ids = Expense.objects.filter(report_id=report_id, org_id=org_id).values_list('id', flat=True)
        expense_groups = ExpenseGroup.objects.filter(expenses__id__in=[expense_ids], workspace_id=workspace.id, exported_at__isnull=True).distinct('id').values('id')
        expense_group_ids = [expense_group['id'] for expense_group in expense_groups]

        if len(expense_group_ids):
            if is_state_change_event:
                # Trigger export immediately for customers who have enabled real time export
                is_real_time_export_enabled = WorkspaceSchedule.objects.filter(workspace_id=workspace.id, is_real_time_export_enabled=True).exists()

                # Don't allow real time export if setting not enabled
                if not is_real_time_export_enabled:
                    return

            logger.info(f'Exporting expenses for workspace {workspace.id} with expense group ids {expense_group_ids}, triggered by {imported_from}')
            export_to_xero(
                workspace_id=workspace.id,
                expense_group_ids=expense_group_ids,
                is_direct_export=True if not is_state_change_event else False,
                triggered_by=imported_from
            )

    except WorkspaceGeneralSettings.DoesNotExist:
        logger.info('Configuration does not exist for workspace_id: %s', workspace.id)

    except Exception:
        if not task_log:
            task_log, _ = TaskLog.objects.update_or_create(workspace_id=workspace.id, type='FETCHING_EXPENSES', defaults={'status': 'IN_PROGRESS'})

        handle_import_exception(task_log)


def update_non_exported_expenses(data: Dict) -> None:
    """
    To update expenses not in COMPLETE, IN_PROGRESS state
    """
    expense_state = None
    org_id = data['org_id']
    expense_id = data['id']
    workspace = Workspace.objects.get(fyle_org_id = org_id)
    expense = Expense.objects.filter(workspace_id=workspace.id, expense_id=expense_id).first()

    if expense:
        if 'state' in expense.accounting_export_summary:
            expense_state = expense.accounting_export_summary['state']
        else:
            expense_state = 'NOT_EXPORTED'

        if expense_state and expense_state not in ['COMPLETE', 'IN_PROGRESS']:
            expense_obj = []
            expense_obj.append(data)
            expense_objects = FyleExpenses().construct_expense_object(expense_obj, expense.workspace_id)
            old_fund_source = expense.fund_source
            new_fund_source = REVERSE_SOURCE_ACCOUNT_MAP[expense_objects[0]['source_account_type']]

            old_category = expense.category if (expense.category == expense.sub_category or expense.sub_category is None) else '{0} / {1}'.format(expense.category, expense.sub_category)
            new_category = expense_objects[0]['category'] if (expense_objects[0]['category'] == expense_objects[0]['sub_category'] or expense_objects[0]['sub_category'] is None) else '{0} / {1}'.format(expense_objects[0]['category'], expense_objects[0]['sub_category'])

            Expense.create_expense_objects(
                expense_objects, expense.workspace_id, skip_update=True
            )

            if old_fund_source != new_fund_source:
                logger.info("Fund source changed for expense %s from %s to %s in workspace %s", expense.id, old_fund_source, new_fund_source, expense.workspace_id)
                handle_fund_source_changes_for_expense_ids(
                    workspace_id=expense.workspace_id,
                    changed_expense_ids=[expense.id],
                    report_id=expense.report_id,
                    affected_fund_source_expense_ids={old_fund_source: [expense.id]}
                )

            if old_category != new_category:
                logger.info("Category changed for expense %s from %s to %s in workspace %s", expense.id, old_category, new_category, expense.workspace_id)
                handle_category_changes_for_expense(expense=expense, new_category=new_category)


def handle_category_changes_for_expense(expense: Expense, new_category: str) -> None:
    """
    Handle category changes for expense
    :param expense: Expense object
    :param new_category: New category
    :return: None
    """
    with transaction.atomic():
        expense_group = ExpenseGroup.objects.filter(expenses__id=expense.id, workspace_id=expense.workspace_id).first()
        if expense_group:
            error = Error.objects.filter(workspace_id=expense.workspace_id, is_resolved=False, type='CATEGORY_MAPPING', mapping_error_expense_group_ids__contains=[expense_group.id]).first()
            if error:
                logger.info('Removing expense group: %s from errors for workspace_id: %s as a result of category update for expense %s', expense_group.id, expense.workspace_id, expense.id)
                error.mapping_error_expense_group_ids.remove(expense_group.id)
                if error.mapping_error_expense_group_ids:
                    error.updated_at = datetime.now(timezone.utc)
                    error.save(update_fields=['mapping_error_expense_group_ids', 'updated_at'])
                else:
                    error.delete()

            new_category_expense_attribute = ExpenseAttribute.objects.filter(workspace_id=expense.workspace_id, attribute_type='CATEGORY', value=new_category).first()
            if new_category_expense_attribute:
                updated_category_error = Error.objects.filter(workspace_id=expense.workspace_id, is_resolved=False, type='CATEGORY_MAPPING', expense_attribute=new_category_expense_attribute).first()
                if updated_category_error:
                    updated_category_error.mapping_error_expense_group_ids.append(expense_group.id)
                    updated_category_error.updated_at = datetime.now(timezone.utc)
                    updated_category_error.save(update_fields=['mapping_error_expense_group_ids', 'updated_at'])
                else:
                    mapping = Mapping.objects.filter(
                        source_type='CATEGORY',
                        destination_type='ACCOUNT',
                        source=new_category_expense_attribute,
                        workspace_id=expense_group.workspace_id
                    ).first()
                    if not mapping:
                        Error.objects.create(
                            workspace_id=expense.workspace_id,
                            type='CATEGORY_MAPPING',
                            expense_attribute=new_category_expense_attribute,
                            mapping_error_expense_group_ids=[expense_group.id],
                            updated_at=datetime.now(timezone.utc),
                            error_detail=f"{new_category_expense_attribute.display_name} mapping is missing",
                            error_title=new_category_expense_attribute.value
                        )


def handle_expense_fund_source_change(workspace_id: int, report_id: str, platform: PlatformConnector) -> None:
    """
    Handle expense fund source change
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param platform: Platform connector
    :return: None
    """
    expenses = platform.expenses.get(
        source_account_type=[SOURCE_ACCOUNT_MAP[FundSourceEnum.PERSONAL], SOURCE_ACCOUNT_MAP[FundSourceEnum.CCC]],
        report_id=report_id,
        filter_credit_expenses=False
    )

    expenses_to_update: List[Dict] = []
    expense_ids_changed: List[int] = []
    expenses_in_db = Expense.objects.filter(workspace_id=workspace_id, report_id=report_id).values_list('expense_id', 'fund_source', 'id')
    expense_id_fund_source_map = {
        expense[0]: {
            'fund_source': expense[1],
            'id': expense[2]
        }
        for expense in expenses_in_db
    }

    affected_fund_source_expense_ids: dict[str, List[int]] = {
        FundSourceEnum.PERSONAL: [],
        FundSourceEnum.CCC: []
    }

    for expense in expenses:
        if expense['id'] in expense_id_fund_source_map:
            new_expense_fund_source = REVERSE_SOURCE_ACCOUNT_MAP[expense['source_account_type']]
            old_expense_fund_source = expense_id_fund_source_map[expense['id']]['fund_source']
            if new_expense_fund_source != old_expense_fund_source:
                logger.info("Expense Fund Source changed for expense %s from %s to %s", expense['id'], old_expense_fund_source, new_expense_fund_source)
                expenses_to_update.append(expense)
                expense_ids_changed.append(expense_id_fund_source_map[expense['id']]['id'])
                affected_fund_source_expense_ids[old_expense_fund_source].append(expense_id_fund_source_map[expense['id']]['id'])

    if expenses_to_update:
        logger.info("Updating Fund Source Change for expenses with report_id %s in workspace %s | COUNT %s", report_id, workspace_id, len(expenses_to_update))
        Expense.create_expense_objects(expenses=expenses_to_update, workspace_id=workspace_id, skip_update=False)
        handle_fund_source_changes_for_expense_ids(workspace_id=workspace_id, changed_expense_ids=expense_ids_changed, report_id=report_id, affected_fund_source_expense_ids=affected_fund_source_expense_ids)


def handle_fund_source_changes_for_expense_ids(workspace_id: int, changed_expense_ids: List[int], report_id: str, affected_fund_source_expense_ids: dict[str, List[int]], task_name: str = None) -> None:
    """
    Main entry point for handling fund_source changes for expense ids
    :param workspace_id: workspace id
    :param changed_expense_ids: List of expense IDs whose fund_source changed
    :param report_id: Report id
    :param affected_fund_source_expense_ids: Dict of affected fund sources and their expense ids
    :param task_name: Name of the task to clean up
    :return: None
    """
    filter_for_affected_expense_groups = construct_filter_for_affected_expense_groups(workspace_id=workspace_id, report_id=report_id, changed_expense_ids=changed_expense_ids, affected_fund_source_expense_ids=affected_fund_source_expense_ids)

    with transaction.atomic():
        affected_groups = ExpenseGroup.objects.filter(
            filter_for_affected_expense_groups,
            workspace_id=workspace_id,
            exported_at__isnull=True
        ).annotate(
            expense_count=Count('expenses')
        ).distinct()

        if not affected_groups:
            logger.info("No expense groups found for changed expenses: %s in workspace %s", changed_expense_ids, workspace_id)
            return

        affected_expense_ids = list(affected_groups.values_list('expenses__id', flat=True))

        are_all_expense_groups_exported = True

        for group in affected_groups:
            logger.info("Processing fund source change for expense group %s with %s expenses in workspace %s", group.id, group.expense_count, workspace_id)
            is_expense_group_processed = process_expense_group_for_fund_source_update(
                expense_group=group,
                changed_expense_ids=changed_expense_ids,
                workspace_id=workspace_id,
                report_id=report_id,
                affected_fund_source_expense_ids=affected_fund_source_expense_ids
            )

            if not is_expense_group_processed:
                are_all_expense_groups_exported = False

        if are_all_expense_groups_exported:
            logger.info("All expense groups are exported or are not initiated, proceeding with recreation of expense groups for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)
            recreate_expense_groups(workspace_id=workspace_id, expense_ids=affected_expense_ids)
            cleanup_scheduled_task(task_name=task_name, workspace_id=workspace_id)
        else:
            logger.info("Not all expense groups are exported, skipping recreation of expense groups for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)
            return


def process_expense_group_for_fund_source_update(expense_group: ExpenseGroup, changed_expense_ids: List[int], workspace_id: int, report_id: str, affected_fund_source_expense_ids: dict[str, List[int]]) -> bool:
    """
    Process individual expense group based on task log state
    :param expense_group: Expense group
    :param changed_expense_ids: List of expense IDs whose fund_source changed
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param affected_fund_source_expense_ids: Dict of affected fund sources and their expense ids
    :return: bool indicating if group can be processed now
    """
    # this is to prevent update the task logs from different transactions
    task_log = TaskLog.objects.select_for_update().filter(
        ~Q(type__in=['CREATING_REIMBURSEMENT', 'CREATING_AP_PAYMENT']),
        expense_group_id=expense_group.id,
        workspace_id=expense_group.workspace_id
    ).order_by('-created_at').first()

    if task_log:
        logger.info("Task log for expense group %s in %s state for workspace %s", expense_group.id, task_log.status, expense_group.workspace_id)
        if task_log.status in ['ENQUEUED', 'IN_PROGRESS']:
            schedule_task_for_expense_group_fund_source_change(changed_expense_ids=changed_expense_ids, workspace_id=workspace_id, report_id=report_id, affected_fund_source_expense_ids=affected_fund_source_expense_ids)
            return False

        elif task_log.status == 'COMPLETE':
            logger.info("Skipping expense group %s - already exported successfully", expense_group.id)
            return False

    logger.info("Proceeding with processing for expense group %s in workspace %s", expense_group.id, expense_group.workspace_id)
    delete_expense_group_and_related_data(expense_group=expense_group, workspace_id=workspace_id)
    return True


def delete_expense_group_and_related_data(expense_group: ExpenseGroup, workspace_id: int) -> None:
    """
    Delete expense group and all related data safely
    :param expense_group: Expense group
    :param workspace_id: Workspace id
    :return: None
    """
    group_id = expense_group.id

    # Delete task logs
    task_logs_deleted = TaskLog.objects.filter(
        ~Q(type__in=['CREATING_REIMBURSEMENT', 'CREATING_AP_PAYMENT']),
        expense_group_id=group_id,
        workspace_id=workspace_id
    ).delete()
    logger.info("Deleted %s task logs for group %s in workspace %s", task_logs_deleted[0], group_id, workspace_id)

    # Delete errors
    errors_deleted = Error.objects.filter(
        expense_group_id=group_id,
        workspace_id=workspace_id
    ).delete()
    logger.info("Deleted %s error logs for group %s in workspace %s", errors_deleted[0], group_id, workspace_id)

    # mapping_error_expense_group_ids in Error model
    error_objects = Error.objects.filter(
        mapping_error_expense_group_ids__contains=[group_id],
        workspace_id=workspace_id
    )
    for error in error_objects:
        logger.info("Removing expensegroup %s from mapping_error_expense_group_ids for error %s in workspace %s", group_id, error.id, workspace_id)
        error.mapping_error_expense_group_ids.remove(group_id)
        if error.mapping_error_expense_group_ids:
            error.save(update_fields=['mapping_error_expense_group_ids'])
        else:
            error.delete()

    # Delete the expense group (this will also delete expense_group_expenses relationships)
    expense_group.delete()
    logger.info("Deleted expense group %s in workspace %s", group_id, workspace_id)


def recreate_expense_groups(workspace_id: int, expense_ids: List[int]) -> None:
    """
    Recreate expense groups using standard grouping logic
    :param workspace_id: Workspace id
    :param expense_ids: List of expense IDs
    :return: None
    """
    logger.info("Recreating expense groups for %s expenses in workspace %s", len(expense_ids), workspace_id)

    expenses = Expense.objects.filter(
        id__in=expense_ids,
        expensegroup__exported_at__isnull=True,
        workspace_id=workspace_id
    )

    if not expenses:
        logger.warning("No expenses found for recreation: %s in workspace %s", expense_ids, workspace_id)
        return

    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    # Delete reimbursable expenses if reimbursable expense settings is not configured
    if not configuration.reimbursable_expenses_object:
        reimbursable_expense_ids = [e.id for e in expenses if e.fund_source == FundSourceEnum.PERSONAL]

        if reimbursable_expense_ids:
            expenses = [e for e in expenses if e.id not in reimbursable_expense_ids]
            delete_expenses_in_db(expense_ids=reimbursable_expense_ids, workspace_id=workspace_id)

    # Delete corporate credit card expenses if corporate credit card expense settings is not configured
    if not configuration.corporate_credit_card_expenses_object:
        ccc_expense_ids = [e.id for e in expenses if e.fund_source == FundSourceEnum.CCC]

        if ccc_expense_ids:
            expenses = [e for e in expenses if e.id not in ccc_expense_ids]
            delete_expenses_in_db(expense_ids=ccc_expense_ids, workspace_id=workspace_id)

    expense_objects = expenses

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        expense_objects, workspace_id
    )

    logger.info("Successfully recreated expense groups for %s expenses in workspace %s", len(expense_ids), workspace_id)


def schedule_task_for_expense_group_fund_source_change(changed_expense_ids: List[int], workspace_id: int, report_id: str, affected_fund_source_expense_ids: dict[str, List[int]]) -> None:
    """
    Schedule expense group for later processing when task logs are no longer active
    :param changed_expense_ids: List of expense IDs whose fund_source changed
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param affected_fund_source_expense_ids: Dict of affected fund sources and their expense ids
    :return: None
    """
    try:
        from django_q.models import Schedule
        from django_q.tasks import schedule
    except ImportError:
        logger.warning("Django Q not available, cannot schedule task for workspace %s", workspace_id)
        return

    logger.info("Scheduling for later processing for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)

    # generate some random string to avoid duplicate tasks
    hashed_name = hashlib.md5(str(changed_expense_ids).encode('utf-8')).hexdigest()[0:6]

    # Check if there's already a scheduled task for this expense group to avoid duplicates
    task_name = f'fund_source_change_retry_{hashed_name}_{workspace_id}'
    existing_schedule = Schedule.objects.filter(
        func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids',
        name=task_name
    ).first()

    if existing_schedule:
        logger.info("Task already scheduled for changed expense ids %s in workspace %s", changed_expense_ids, workspace_id)
        return

    schedule_time = datetime.now() + timedelta(minutes=5)

    schedule(
        'apps.fyle.tasks.handle_fund_source_changes_for_expense_ids',
        workspace_id,
        changed_expense_ids,
        report_id,
        affected_fund_source_expense_ids,
        task_name,
        repeats=10,  # 10 retries
        schedule_type='M',  # Minute
        minutes=5,  # 5 minutes delay
        timeout=300,  # 5 minutes timeout
        next_run=schedule_time,
        name=task_name
    )

    logger.info("Scheduled delayed processing for changed expense ids %s in workspace %s with name %s", changed_expense_ids, workspace_id, task_name)


def cleanup_scheduled_task(task_name: str, workspace_id: int) -> None:
    """
    Clean up scheduled task
    :param task_name: Name of the task to clean up
    :param workspace_id: Workspace id
    :return: None
    """
    try:
        from django_q.models import Schedule
    except ImportError:
        logger.warning("Django Q not available, cannot cleanup task for workspace %s", workspace_id)
        return

    logger.info("Cleaning up scheduled task %s in workspace %s", task_name, workspace_id)

    schedule_obj = Schedule.objects.filter(name=task_name, func='apps.fyle.tasks.handle_fund_source_changes_for_expense_ids').first()
    if schedule_obj:
        schedule_obj.delete()
        logger.info("Cleaned up scheduled task: %s", task_name)
    else:
        logger.info("No scheduled task found to clean up: %s", task_name)


def delete_expenses_in_db(expense_ids: List[int], workspace_id: int) -> None:
    """
    Delete expenses in database
    :param expense_ids: List of expense IDs
    :param workspace_id: Workspace id
    :return: None
    """
    deleted_count = Expense.objects.filter(id__in=expense_ids, workspace_id=workspace_id).delete()[0]
    logger.info("Deleted %s expenses in workspace %s", deleted_count, workspace_id)


def handle_expense_report_change(expense_data: dict, action_type: str) -> None:
    """
    Handle expense report changes (EJECTED_FROM_REPORT, ADDED_TO_REPORT)
    :param expense_data: Expense data from webhook
    :param action_type: Type of action (EJECTED_FROM_REPORT or ADDED_TO_REPORT)
    :return: None
    """
    org_id = expense_data['org_id']
    expense_id = expense_data['id']
    workspace = Workspace.objects.get(fyle_org_id=org_id)

    if action_type == 'ADDED_TO_REPORT':
        report_id = expense_data.get('report_id')

        logger.info("Processing ADDED_TO_REPORT for expense %s in workspace %s, report_id: %s", expense_id, workspace.id, report_id)
        _delete_expense_groups_for_report(report_id, workspace)
        return

    elif action_type == 'EJECTED_FROM_REPORT':
        expense = Expense.objects.filter(workspace_id=workspace.id, expense_id=expense_id).first()

        if not expense:
            logger.warning("Expense %s not found in workspace %s for action %s", expense_id, workspace.id, action_type)
            return

        expense_group = ExpenseGroup.objects.filter(
            expenses=expense,
            workspace_id=workspace.id,
            exported_at__isnull=False
        ).first()

        if expense_group:
            logger.info("Skipping %s for expense %s as it's part of exported expense group %s", action_type, expense_id, expense_group.id)
            return

        logger.info("Processing %s for expense %s in workspace %s", action_type, expense_id, workspace.id)
        _handle_expense_ejected_from_report(expense, expense_data, workspace)


def _delete_expense_groups_for_report(report_id: str, workspace: Workspace) -> None:
    """
    Delete all non-exported expense groups for a report
    When expenses are added to a report, the report goes to SUBMITTED state which is not importable.
    This function deletes all expense groups for the report so they can be recreated when the report
    changes to an importable state (APPROVED/PAYMENT_PROCESSING/PAID) via state change webhook.

    :param report_id: Report ID
    :param workspace: Workspace object
    :return: None
    """
    logger.info("Deleting expense groups for report %s in workspace %s", report_id, workspace.id)

    expense_ids = Expense.objects.filter(
        workspace_id=workspace.id,
        report_id=report_id
    ).values_list('id', flat=True)

    if not expense_ids:
        logger.info("No expenses found for report %s in workspace %s", report_id, workspace.id)
        return

    expense_groups = ExpenseGroup.objects.filter(
        expenses__id__in=expense_ids,
        workspace_id=workspace.id,
        exported_at__isnull=True
    ).distinct()

    deleted_count = 0
    skipped_count = 0

    for expense_group in expense_groups:
        active_task_logs = TaskLog.objects.filter(
            expense_group_id=expense_group.id,
            workspace_id=workspace.id,
            status__in=['ENQUEUED', 'IN_PROGRESS']
        ).exists()

        if active_task_logs:
            logger.warning("Skipping deletion of expense group %s - active task logs exist", expense_group.id)
            skipped_count += 1
            continue

        logger.info("Deleting expense group %s for report %s", expense_group.id, report_id)

        with transaction.atomic():
            delete_expense_group_and_related_data(expense_group, workspace.id)

        deleted_count += 1

    logger.info("Completed deletion for report %s in workspace %s - deleted: %s, skipped: %s",
                report_id, workspace.id, deleted_count, skipped_count)


def _handle_expense_ejected_from_report(expense: Expense, expense_data: dict, workspace: Workspace) -> None:
    """
    Handle expense ejected from report
    :param expense: Expense object
    :param expense_data: Expense data from webhook
    :param workspace: Workspace object
    :return: None
    """
    logger.info("Handling expense %s ejected from report in workspace %s", expense.expense_id, workspace.id)

    expense_group = ExpenseGroup.objects.filter(
        expenses=expense,
        workspace_id=workspace.id,
        exported_at__isnull=True
    ).first()

    if not expense_group:
        logger.info("No expense group found for expense %s in workspace %s", expense.expense_id, workspace.id)
        return

    logger.info("Removing expense %s from expense group %s", expense.expense_id, expense_group.id)

    active_task_logs = TaskLog.objects.filter(
        expense_group_id=expense_group.id,
        workspace_id=workspace.id,
        status__in=['ENQUEUED', 'IN_PROGRESS']
    ).exists()

    if active_task_logs:
        logger.warning("Cannot remove expense %s from group %s - active task logs exist", expense.expense_id, expense_group.id)
        return

    with transaction.atomic():
        expense_group.expenses.remove(expense)

        if not expense_group.expenses.exists():
            logger.info("Deleting empty expense group %s after removing expense %s", expense_group.id, expense.expense_id)
            delete_expense_group_and_related_data(expense_group, workspace.id)
        else:
            logger.info("Expense group %s still has expenses after removing %s", expense_group.id, expense.expense_id)


def get_grouping_types(workspace_id: int) -> dict[str, str]:
    """
    Get grouping types for a workspace
    :param workspace_id: Workspace id
    :return: Dict of grouping types
    """
    grouping_types = {}

    expense_group_settings = ExpenseGroupSettings.objects.filter(workspace_id=workspace_id).first()

    if expense_group_settings:
        reimbursable_grouping_type = 'report' if 'report_id' in expense_group_settings.reimbursable_expense_group_fields else 'expense'
        ccc_grouping_type = 'report' if 'report_id' in expense_group_settings.corporate_credit_card_expense_group_fields else 'expense'

        grouping_types = {
            FundSourceEnum.PERSONAL: reimbursable_grouping_type,
            FundSourceEnum.CCC: ccc_grouping_type
        }

    return grouping_types


def handle_org_setting_updated(workspace_id: int, org_settings: dict) -> None:
    """
    Update regional date setting on org setting updated
    :param workspace_id: Workspace id
    :param org_settings: Org settings
    :return: None
    """
    logger.info("Handling org settings update for workspace %s", workspace_id)

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.org_settings = {
        'regional_settings': org_settings.get('regional_settings', {})
    }
    workspace.save(update_fields=['org_settings', 'updated_at'])
    logger.info("Updated org settings for workspace %s", workspace.id)


def construct_filter_for_affected_expense_groups(workspace_id: int, report_id: str, changed_expense_ids: List[int], affected_fund_source_expense_ids: dict[str, List[int]]) -> Q:
    """
    Construct filter for affected expense groups
    :param workspace_id: Workspace id
    :param report_id: Report id
    :param changed_expense_ids: List of changed expense ids
    :param affected_fund_source_expense_ids: Dict of affected fund source and their expense ids
    :return: Filter for affected expense groups
    """
    grouping_types = get_grouping_types(workspace_id=workspace_id)
    filter_for_affected_expense_groups = Q()

    if grouping_types.get(FundSourceEnum.PERSONAL) == 'report' and grouping_types.get(FundSourceEnum.CCC) == 'report':
        filter_for_affected_expense_groups = Q(
            expenses__report_id=report_id
        )
    elif grouping_types.get(FundSourceEnum.PERSONAL) == 'expense' and grouping_types.get(FundSourceEnum.CCC) == 'expense':
        filter_for_affected_expense_groups = Q(
            expenses__id__in=changed_expense_ids
        )

    for fund_source, expense_ids in affected_fund_source_expense_ids.items():
        if fund_source == FundSourceEnum.PERSONAL:
            if grouping_types.get(FundSourceEnum.PERSONAL) == 'report' and grouping_types.get(FundSourceEnum.CCC) == 'expense':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source=FundSourceEnum.PERSONAL)
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)
            elif grouping_types.get(FundSourceEnum.PERSONAL) == 'expense' and grouping_types.get(FundSourceEnum.CCC) == 'report':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source=FundSourceEnum.CCC)
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)
        else:
            if grouping_types.get(FundSourceEnum.PERSONAL) == 'report' and grouping_types.get(FundSourceEnum.CCC) == 'expense':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source=FundSourceEnum.CCC)
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)
            elif grouping_types.get(FundSourceEnum.PERSONAL) == 'expense' and grouping_types.get(FundSourceEnum.CCC) == 'report':
                filter_for_affected_expense_groups |= Q(expenses__report_id=report_id, fund_source=FundSourceEnum.PERSONAL)
                filter_for_affected_expense_groups |= Q(expenses__id__in=expense_ids)

    return filter_for_affected_expense_groups
