import logging
from datetime import datetime

from django.conf import settings
from django.db.models import Q
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_integrations_platform_connector import PlatformConnector
from fyle_rest_auth.helpers import get_fyle_admin

from apps.fyle.enums import FundSourceEnum
from apps.fyle.helpers import post_request
from apps.fyle.models import ExpenseGroup
from apps.fyle.tasks import create_expense_groups
from apps.mappings.models import TenantMapping
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import TaskLog
from apps.users.models import User
from apps.workspaces.actions import export_to_xero
from apps.workspaces.email import get_admin_name, get_errors, get_failed_task_logs_count, send_failure_notification_email
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings, WorkspaceSchedule

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

    create_expense_groups(
        workspace_id=workspace_id, fund_source=fund_source, task_log=task_log, imported_from=ExpenseImportSourceEnum.BACKGROUND_SCHEDULE
    )

    if task_log.status == TaskLogStatusEnum.COMPLETE:
        eligible_expense_group_ids = ExpenseGroup.objects.filter(
            workspace_id=workspace_id,
            exported_at__isnull=True
        ).filter(
            Q(tasklog__isnull=True)
            | Q(tasklog__type__in=[TaskLogTypeEnum.CREATING_BILL, TaskLogTypeEnum.CREATING_BANK_TRANSACTION])
        ).exclude(
            tasklog__status=TaskLogStatusEnum.FAILED,
            tasklog__re_attempt_export=False
        ).values_list('id', flat=True).distinct()

        if eligible_expense_group_ids.exists():
            export_to_xero(workspace_id, expense_group_ids=list(eligible_expense_group_ids), triggered_by=ExpenseImportSourceEnum.BACKGROUND_SCHEDULE)


def async_update_fyle_credentials(fyle_org_id: str, refresh_token: str):
    fyle_credentials = FyleCredential.objects.filter(
        workspace__fyle_org_id=fyle_org_id
    ).first()
    if fyle_credentials and refresh_token:
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


def async_create_admin_subscriptions(workspace_id: int) -> None:
    """
    Create admin subscriptions
    :param workspace_id: workspace id
    :return: None
    """
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)
    payload = {
        'is_enabled': True,
        'webhook_url': '{}/workspaces/{}/fyle/exports/'.format(settings.API_URL, workspace_id),
        'subscribed_resources': [
            'EXPENSE',
            'REPORT',
            'CATEGORY',
            'PROJECT',
            'COST_CENTER',
            'EXPENSE_FIELD',
            'CORPORATE_CARD',
            'EMPLOYEE',
            'TAX_GROUP',
            'ORG_SETTING'
        ]
    }
    platform.subscriptions.post(payload)


def post_to_integration_settings(workspace_id: int, active: bool):
    """
    Post to integration settings
    """
    refresh_token = FyleCredential.objects.get(workspace_id=workspace_id).refresh_token
    url = '{}/integrations/'.format(settings.INTEGRATIONS_SETTINGS_API)
    payload = {
        'tpa_id': settings.FYLE_CLIENT_ID,
        'tpa_name': 'Fyle Xero Integration',
        'type': 'ACCOUNTING',
        'is_active': active,
        'connected_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    try:
        post_request(url, payload, refresh_token)
    except Exception as error:
        logger.error(error)
