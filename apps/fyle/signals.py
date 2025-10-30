import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum, FundSourceEnum

from apps.fyle.enums import ExpenseStateEnum
from apps.fyle.models import ExpenseGroupSettings
from apps.workspaces.models import WorkspaceGeneralSettings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@receiver(post_save, sender=ExpenseGroupSettings)
def run_post_save_expense_group_setting_triggers(sender, instance: ExpenseGroupSettings, **kwargs):
    """
    Run post save expense group setting triggers
    """
    existing_expense_group_setting = ExpenseGroupSettings.objects.filter(
        workspace_id=instance.workspace_id
    ).first()

    if existing_expense_group_setting:
        configuration = WorkspaceGeneralSettings.objects.filter(workspace_id=instance.workspace_id).first()
        if configuration:
            # TODO: move these async_tasks to maintenance worker later
            if configuration.reimbursable_expenses_object and existing_expense_group_setting.reimbursable_expense_state != instance.reimbursable_expense_state and existing_expense_group_setting.reimbursable_expense_state == ExpenseStateEnum.PAID and instance.reimbursable_expense_state == ExpenseStateEnum.PAYMENT_PROCESSING:
                logger.info(f'Reimbursable expense state changed from {existing_expense_group_setting.reimbursable_expense_state} to {instance.reimbursable_expense_state} for workspace {instance.workspace_id}, so pulling the data from Fyle')
                async_task('apps.fyle.tasks.create_expense_groups', workspace_id=instance.workspace_id, task_log=None, fund_source=[FundSourceEnum.PERSONAL], imported_from=ExpenseImportSourceEnum.CONFIGURATION_UPDATE)

            if configuration.corporate_credit_card_expenses_object and existing_expense_group_setting.ccc_expense_state != instance.ccc_expense_state and existing_expense_group_setting.ccc_expense_state == ExpenseStateEnum.PAID and instance.ccc_expense_state == ExpenseStateEnum.APPROVED:
                logger.info(f'Corporate credit card expense state changed from {existing_expense_group_setting.ccc_expense_state} to {instance.ccc_expense_state} for workspace {instance.workspace_id}, so pulling the data from Fyle')
                async_task('apps.fyle.tasks.create_expense_groups', workspace_id=instance.workspace_id, task_log=None, fund_source=[FundSourceEnum.CCC], imported_from=ExpenseImportSourceEnum.CONFIGURATION_UPDATE)
