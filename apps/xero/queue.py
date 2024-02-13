from datetime import datetime, timedelta

from django_q.models import Schedule
from typing import List

from django.db.models import Q

from django_q.tasks import Chain


from xerosdk.exceptions import UnsuccessfulAuthentication

from apps.fyle.models import Expense, ExpenseGroup

from apps.mappings.models import GeneralMapping

from apps.tasks.models import TaskLog
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum

from apps.workspaces.models import FyleCredential, XeroCredentials

from apps.xero.utils import XeroConnector


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


def __create_chain_and_run(fyle_credentials: FyleCredential, xero_connection, in_progress_expenses: List[Expense],
        workspace_id: int, chain_tasks: List[dict], fund_source: str) -> None:
    """
    Create chain and run
    :param fyle_credentials: Fyle credentials
    :param in_progress_expenses: List of in progress expenses
    :param workspace_id: workspace id
    :param chain_tasks: List of chain tasks
    :param fund_source: Fund source
    :return: None
    """
    chain = Chain()
    chain.append("apps.fyle.tasks.sync_dimensions", fyle_credentials)

    chain.append('apps.xero.tasks.update_expense_and_post_summary', in_progress_expenses, workspace_id, fund_source)

    for task in chain_tasks:
        chain.append(task['target'], task['expense_group_id'], task['task_log_id'], xero_connection, task['last_export'])

    chain.append('apps.fyle.tasks.post_accounting_export_summary', fyle_credentials.workspace.fyle_org_id, workspace_id, fund_source)
    chain.run()


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, fund_source: str) -> list:
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

        chain_tasks = []
        in_progress_expenses = []

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={"status": TaskLogStatusEnum.ENQUEUED, "type": TaskLogTypeEnum.CREATING_BILL},
            )
            if task_log.status not in [TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.ENQUEUED]:
                task_log.status = TaskLogStatusEnum.ENQUEUED
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain_tasks.append({
                'target': 'apps.xero.tasks.create_bill',
                'expense_group_id': expense_group.id,
                'task_log_id': task_log.id,
                'last_export': last_export})

            if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
                in_progress_expenses.extend(expense_group.expenses.all())

        if len(chain_tasks) > 0:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            try:
                xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
                xero_connection = XeroConnector(xero_credentials, workspace_id)
                __create_chain_and_run(fyle_credentials, xero_connection, in_progress_expenses, workspace_id, chain_tasks, fund_source)
            except (UnsuccessfulAuthentication, XeroCredentials.DoesNotExist):
                xero_connection = None


def schedule_bank_transaction_creation(
    workspace_id: int, expense_group_ids: List[str], is_auto_export: bool, fund_source: str
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

        chain_tasks = []
        in_progress_expenses = []

        for index, expense_group in enumerate(expense_groups):
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={"status": TaskLogStatusEnum.ENQUEUED, "type": TaskLogTypeEnum.CREATING_BANK_TRANSACTION},
            )
            if task_log.status not in [TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.ENQUEUED]:
                task_log.status = TaskLogStatusEnum.ENQUEUED
                task_log.save()

            last_export = False
            if expense_groups.count() == index + 1:
                last_export = True

            chain_tasks.append({
                'target': 'apps.xero.tasks.create_bank_transaction',
                'expense_group_id': expense_group.id,
                'task_log_id': task_log.id,
                'last_export': last_export})

            if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
                in_progress_expenses.extend(expense_group.expenses.all())

        if len(chain_tasks) > 0:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
            try:
                xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
                xero_connection = XeroConnector(xero_credentials, workspace_id)
            except (UnsuccessfulAuthentication, XeroCredentials.DoesNotExist):
                xero_connection = None
            __create_chain_and_run(fyle_credentials, xero_connection, in_progress_expenses, workspace_id, chain_tasks, fund_source)
