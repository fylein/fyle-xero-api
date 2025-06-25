import logging
from datetime import datetime, timedelta, timezone
from typing import List

from django.db.models import Q
from django_q.models import Schedule
from django_q.tasks import Chain
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_library.rabbitmq.helpers import TaskChainRunner
from fyle_accounting_library.rabbitmq.data_class import Task

from apps.fyle.actions import post_accounting_export_summary_for_skipped_exports, sync_fyle_dimension
from apps.fyle.models import ExpenseGroup
from apps.mappings.models import GeneralMapping
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import Error, TaskLog
from apps.xero.exceptions import update_last_export_details


logger = logging.getLogger(__name__)
logger.level = logging.INFO


def validate_failing_export(is_auto_export: bool, interval_hours: int, error: Error, expense_group: ExpenseGroup):
    """
    Validate failing export
    :param is_auto_export: Is auto export
    :param interval_hours: Interval hours
    :param error: Error
    """
    mapping_error = Error.objects.filter(
        workspace_id=expense_group.workspace_id,
        mapping_error_expense_group_ids__contains=[expense_group.id],
        is_resolved=False
    ).first()
    if mapping_error:
        return True

    # If auto export is enabled and interval hours is set and error repetition count is greater than 100, export only once a day
    return is_auto_export and interval_hours and error and error.repetition_count > 100 and datetime.now().replace(tzinfo=timezone.utc) - error.updated_at <= timedelta(hours=24)


def schedule_payment_creation(sync_fyle_to_xero_payments, workspace_id):
    general_mappings: GeneralMapping = GeneralMapping.objects.filter(
        workspace_id=workspace_id
    ).first()
    if general_mappings:
        if sync_fyle_to_xero_payments and general_mappings.payment_account_id:
            start_datetime = datetime.now()
            schedule, _ = Schedule.objects.update_or_create(
                func="apps.xero.tasks.create_payment",
                args="{}".format(workspace_id),
                defaults={
                    "schedule_type": Schedule.MINUTES,
                    "minutes": 24 * 60,
                    "next_run": start_datetime,
                },
            )
    if not sync_fyle_to_xero_payments:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.xero.tasks.create_payment", args="{}".format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_xero_objects_status_sync(sync_xero_to_fyle_payments, workspace_id):
    if sync_xero_to_fyle_payments:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.xero.tasks.check_xero_object_status",
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.xero.tasks.check_xero_object_status",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_reimbursements_sync(sync_xero_to_fyle_payments, workspace_id):
    if sync_xero_to_fyle_payments:
        start_datetime = datetime.now() + timedelta(hours=12)
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.xero.tasks.process_reimbursements",
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.xero.tasks.process_reimbursements",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def __create_chain_and_run(workspace_id: int, chain_tasks: List[Task], is_auto_export: bool, run_in_rabbitmq_worker: bool) -> None:
    """
    Create chain and run
    :param workspace_id: workspace id
    :param xero_connection: Xero connection
    :param chain_tasks: List of Task objects
    :return: None
    """
    if run_in_rabbitmq_worker:
        # This function checks intervals and triggers sync if needed, syncing dimension for all exports is overkill
        sync_fyle_dimension(workspace_id)

        task_executor = TaskChainRunner()
        task_executor.run(chain_tasks, workspace_id)
    else:
        chain = Chain()
        chain.append('apps.fyle.actions.sync_fyle_dimension', workspace_id)

        for task in chain_tasks:
            chain.append(task.target, *task.args)

        chain.run()


def handle_skipped_exports(expense_groups: List[ExpenseGroup], index: int, skip_export_count: int, error: Error = None, expense_group: ExpenseGroup = None, triggered_by: ExpenseImportSourceEnum = None):
    """
    Handle common export scheduling logic for skip tracking, logging, posting skipped export summaries, and last export updates.
    """
    total_count = expense_groups.count()
    last_export = (index + 1) == total_count

    skip_reason = f"{error.repetition_count} repeated attempts" if error else "mapping errors"
    logger.info(f"Skipping expense group {expense_group.id} due to {skip_reason}")
    skip_export_count += 1
    if triggered_by == ExpenseImportSourceEnum.DIRECT_EXPORT:
        post_accounting_export_summary_for_skipped_exports(
            expense_group, expense_group.workspace_id, is_mapping_error=False if error else True
        )
    if last_export and skip_export_count == total_count:
        update_last_export_details(expense_group.workspace_id)

    return skip_export_count


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, interval_hours: int, triggered_by: ExpenseImportSourceEnum, run_in_rabbitmq_worker: bool) -> list:
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: List of chaining attributes
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True)
            | ~Q(tasklog__status__in=[TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.COMPLETE]),
            workspace_id=workspace_id,
            id__in=expense_group_ids,
            bill__id__isnull=True,
            exported_at__isnull=True,
        ).all()

        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False, expense_group_id__in=expense_group_ids).all()

        chain_tasks = []
        skip_export_count = 0

        for index, expense_group in enumerate(expense_groups):
            error = errors.filter(workspace_id=workspace_id, expense_group=expense_group, is_resolved=False).first()
            skip_export = validate_failing_export(is_auto_export, interval_hours, error, expense_group)
            if skip_export:
                skip_export_count = handle_skipped_exports(
                    expense_groups=expense_groups, index=index, skip_export_count=skip_export_count,
                    error=error, expense_group=expense_group, triggered_by=triggered_by
                )
                continue

            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={"status": TaskLogStatusEnum.ENQUEUED, "type": TaskLogTypeEnum.CREATING_BILL, 'triggered_by': triggered_by},
            )
            if task_log.status not in [TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.ENQUEUED]:
                task_log.type = TaskLogTypeEnum.CREATING_BILL
                task_log.status = TaskLogStatusEnum.ENQUEUED
                if triggered_by and task_log.triggered_by != triggered_by:
                    task_log.triggered_by = triggered_by

                task_log.save()

            chain_tasks.append(Task(
                target='apps.xero.tasks.create_bill',
                args=[expense_group.id, task_log.id, (expense_groups.count() == index + 1), is_auto_export]
            ))

        if len(chain_tasks) > 0:
            __create_chain_and_run(workspace_id, chain_tasks, is_auto_export, run_in_rabbitmq_worker)


def schedule_bank_transaction_creation(
    workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, interval_hours: int, triggered_by: ExpenseImportSourceEnum, run_in_rabbitmq_worker: bool
) -> list:
    """
    Schedule bank transaction creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: List of chaining attributes
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True)
            | ~Q(tasklog__status__in=[TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.COMPLETE]),
            workspace_id=workspace_id,
            id__in=expense_group_ids,
            banktransaction__id__isnull=True,
            exported_at__isnull=True,
        ).all()

        errors = Error.objects.filter(workspace_id=workspace_id, is_resolved=False, expense_group_id__in=expense_group_ids).all()

        chain_tasks = []
        skip_export_count = 0

        for index, expense_group in enumerate(expense_groups):
            error = errors.filter(workspace_id=workspace_id, expense_group=expense_group, is_resolved=False).first()
            skip_export = validate_failing_export(is_auto_export, interval_hours, error, expense_group)
            if skip_export:
                skip_export_count = handle_skipped_exports(
                    expense_groups=expense_groups, index=index, skip_export_count=skip_export_count,
                    error=error, expense_group=expense_group, triggered_by=triggered_by
                )
                continue

            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={"status": TaskLogStatusEnum.ENQUEUED, "type": TaskLogTypeEnum.CREATING_BANK_TRANSACTION, 'triggered_by': triggered_by},
            )
            if task_log.status not in [TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.ENQUEUED]:
                task_log.type = TaskLogTypeEnum.CREATING_BANK_TRANSACTION
                task_log.status = TaskLogStatusEnum.ENQUEUED
                if triggered_by and task_log.triggered_by != triggered_by:
                    task_log.triggered_by = triggered_by

                task_log.save()

            chain_tasks.append(Task(
                target='apps.xero.tasks.create_bank_transaction',
                args=[expense_group.id, task_log.id, (expense_groups.count() == index + 1), is_auto_export]
            ))

        if len(chain_tasks) > 0:
            __create_chain_and_run(workspace_id, chain_tasks, is_auto_export, run_in_rabbitmq_worker)