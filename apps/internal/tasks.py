import logging
from datetime import datetime, timedelta, timezone

from django.db.models import Q
from django_q.models import OrmQ, Schedule
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum

from apps.fyle.actions import update_failed_expenses
from apps.fyle.models import ExpenseGroup
from apps.tasks.models import TaskLog
from apps.workspaces.actions import export_to_xero
from apps.workspaces.models import Workspace

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def re_export_stuck_exports():
    prod_workspace_ids = Workspace.objects.filter(
        ~Q(name__icontains='fyle for') & ~Q(name__iendswith='test')
    ).values_list('id', flat=True)
    task_logs = TaskLog.objects.filter(
        status__in=['ENQUEUED', 'IN_PROGRESS'],
        updated_at__lt=datetime.now() - timedelta(minutes=60),
        expense_group_id__isnull=False,
        workspace_id__in=prod_workspace_ids
    )
    if task_logs.count() > 0:
        logger.info('Re-exporting stuck task_logs')
        logger.info('%s stuck task_logs found', task_logs.count())
        workspace_ids = task_logs.values_list('workspace_id', flat=True).distinct()
        expense_group_ids = task_logs.values_list('expense_group_id', flat=True)
        ormqs = OrmQ.objects.all()
        for orm in ormqs:
            if 'chain' in orm.task and orm.task['chain']:
                for chain in orm.task['chain']:
                    if len(chain) > 1 and isinstance(chain[1], list) and isinstance(chain[1][0], ExpenseGroup):
                        if chain[1][0].id in expense_group_ids:
                            logger.info('Skipping Re Export For Expense group %s', chain[1][0].id)
                            expense_group_ids.remove(chain[1][0].id)

        logger.info('Re-exporting Expense Group IDs: %s', expense_group_ids)
        expense_groups = ExpenseGroup.objects.filter(id__in=expense_group_ids)
        expenses = []
        for expense_group in expense_groups:
            expenses.extend(expense_group.expenses.all())
        workspace_ids_list = list(workspace_ids)
        task_logs.update(status='FAILED', updated_at=datetime.now(timezone.utc))
        update_failed_expenses(expenses, True)
        schedules = Schedule.objects.filter(
            args__in=[str(workspace_id) for workspace_id in workspace_ids_list],
            func='apps.workspaces.tasks.run_sync_schedule'
        )
        for workspace_id in workspace_ids_list:
            logger.info('Checking if 1hour sync schedule for workspace %s', workspace_id)
            schedule = schedules.filter(args=str(workspace_id)).first()
            # If schedule exist and it's within 1 hour, need not trigger it immediately
            if not (schedule and schedule.next_run < datetime.now(tz=schedule.next_run.tzinfo) + timedelta(minutes=60)):
                export_expense_group_ids = expense_groups.filter(workspace_id=workspace_id).values_list('id', flat=True)
                logger.info('Re-triggering export for expense group %s since no 1 hour schedule for workspace  %s', export_expense_group_ids, workspace_id)
                export_to_xero(workspace_id, 'AUTO', export_expense_group_ids, ExpenseImportSourceEnum.RETRY_SCHEDULE)
