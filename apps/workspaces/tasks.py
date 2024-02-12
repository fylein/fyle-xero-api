import logging
from datetime import datetime

from fyle_integrations_platform_connector import PlatformConnector
from fyle_rest_auth.helpers import get_fyle_admin

from apps.fyle.models import ExpenseGroup
from apps.fyle.tasks import async_create_expense_groups
from apps.fyle.enums import FundSourceEnum

from apps.mappings.models import TenantMapping

from apps.tasks.models import TaskLog
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum

from apps.users.models import User

from apps.workspaces.email import get_admin_name, get_errors, get_failed_task_logs_count, send_failure_notification_email
from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, WorkspaceGeneralSettings, WorkspaceSchedule

from apps.xero.tasks import create_chain_and_export, schedule_bank_transaction_creation, schedule_bills_creation


logger = logging.getLogger(__name__)
logger.level = logging.INFO


def run_sync_schedule(workspace_id):
    """
    Run schedule
    :param user: user email
    :param workspace_id: workspace id
    :return: None
    """
    task_log, _ = TaskLog.objects.update_or_create(
        workspace_id=workspace_id,
        type=TaskLogTypeEnum.FETCHING_EXPENSES,
        defaults={"status": TaskLogStatusEnum.IN_PROGRESS}
    )

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)

    fund_source = []
    if general_settings.reimbursable_expenses_object:
        fund_source.append(FundSourceEnum.PERSONAL)
    if general_settings.corporate_credit_card_expenses_object:
        fund_source.append(FundSourceEnum.CCC)

    async_create_expense_groups(
        workspace_id=workspace_id, fund_source=fund_source, task_log=task_log
    )

    if task_log.status == TaskLogStatusEnum.COMPLETE:
        export_to_xero(workspace_id, "AUTO")


def export_to_xero(workspace_id, export_mode="MANUAL"):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    last_exported_at = datetime.now()
    chaining_attributes = []

    if general_settings.reimbursable_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(
            fund_source=FundSourceEnum.PERSONAL,
            workspace_id=workspace_id
        ).values_list("id", flat=True)
        chaining_attributes.extend(
            schedule_bills_creation(workspace_id, expense_group_ids)
        )

    if general_settings.corporate_credit_card_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(
            fund_source=FundSourceEnum.CCC,
            workspace_id=workspace_id
        ).values_list("id", flat=True)
        chaining_attributes.extend(
            schedule_bank_transaction_creation(workspace_id, expense_group_ids)
        )

    if chaining_attributes:
        create_chain_and_export(chaining_attributes, workspace_id)
        last_export_detail.last_exported_at = last_exported_at
        last_export_detail.export_mode = export_mode
        last_export_detail.save()


def async_update_fyle_credentials(fyle_org_id: str, refresh_token: str):
    fyle_credentials = FyleCredential.objects.filter(
        workspace__fyle_org_id=fyle_org_id
    ).first()
    if fyle_credentials:
        fyle_credentials.refresh_token = refresh_token
        fyle_credentials.save()


def run_email_notification(workspace_id):
    ws_schedule = WorkspaceSchedule.objects.get(workspace_id=workspace_id, enabled=True)
    task_logs_count = get_failed_task_logs_count(workspace_id)
    workspace = Workspace.objects.get(id=workspace_id)
    tenant_detail = TenantMapping.get_tenant_details(workspace_id)
    try:
        if task_logs_count and (
            ws_schedule.error_count is None or task_logs_count > ws_schedule.error_count
        ):
            errors = get_errors(workspace_id)
            for admin_email in ws_schedule.emails_selected:
                admin_name = get_admin_name(workspace_id, admin_email, ws_schedule)
                send_failure_notification_email(
                    admin_name,
                    admin_email,
                    task_logs_count,
                    workspace,
                    tenant_detail,
                    errors,
                )

            ws_schedule.error_count = task_logs_count
            ws_schedule.save()

    except Exception as e:
        logger.info('Error in sending email notification: %s', str(e))


def async_add_admins_to_workspace(workspace_id: int, current_user_id: str):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    users = []
    admins = platform.employees.get_admins()

    for admin in admins:
        # Skip current user since it is already added
        if current_user_id != admin["user_id"]:
            users.append(
                User(
                    email=admin["email"],
                    user_id=admin["user_id"],
                    full_name=admin["full_name"],
                )
            )

    if len(users):
        created_users = User.objects.bulk_create(users, batch_size=50)
        workspace = Workspace.objects.get(id=workspace_id)

        for user in created_users:
            workspace.user.add(user)


def async_update_workspace_name(workspace: Workspace, access_token: str):
    fyle_user = get_fyle_admin(access_token.split(' ')[1], None)
    org_name = fyle_user['data']['org']['name']

    workspace.name = org_name
    workspace.save()
