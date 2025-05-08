import logging
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django_q.tasks import async_task
from fyle_accounting_library.fyle_platform.enums import ExpenseImportSourceEnum
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_rest_auth.helpers import get_fyle_admin
from fyle_rest_auth.models import AuthToken
from xerosdk import exceptions as xero_exc

from apps.exceptions import invalidate_xero_credentials
from apps.fyle.actions import post_accounting_export_summary, update_expenses_in_progress
from apps.fyle.enums import FundSourceEnum
from apps.fyle.helpers import get_cluster_domain
from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.mappings.models import TenantMapping
from apps.workspaces.helpers import patch_integration_settings
from apps.workspaces.models import (
    FyleCredential,
    LastExportDetail,
    Workspace,
    WorkspaceGeneralSettings,
    WorkspaceSchedule,
    XeroCredentials,
)
from apps.workspaces.signals import post_delete_xero_connection
from apps.workspaces.utils import generate_xero_refresh_token
from apps.xero.exceptions import update_failed_expenses
from apps.xero.queue import schedule_bank_transaction_creation, schedule_bills_creation
from apps.xero.utils import XeroConnector

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def post_workspace(access_token, request):
    fyle_user = get_fyle_admin(access_token.split(" ")[1], None)
    org_name = fyle_user["data"]["org"]["name"]
    org_id = fyle_user["data"]["org"]["id"]
    fyle_currency = fyle_user["data"]["org"]["currency"]
    User = get_user_model()

    workspace = Workspace.objects.filter(fyle_org_id=org_id).first()

    if workspace:
        workspace.user.add(User.objects.get(user_id=request.user))
        workspace.name = org_name
        workspace.save()
        cache.delete(str(workspace.id))
    else:
        workspace = Workspace.objects.create(
            name=org_name, fyle_currency=fyle_currency, fyle_org_id=org_id
        )

        ExpenseGroupSettings.objects.create(workspace_id=workspace.id)

        LastExportDetail.objects.create(workspace_id=workspace.id)

        workspace.user.add(User.objects.get(user_id=request.user))

        auth_tokens = AuthToken.objects.get(user__user_id=request.user)

        cluster_domain = get_cluster_domain(auth_tokens.refresh_token)

        FyleCredential.objects.update_or_create(
            refresh_token=auth_tokens.refresh_token,
            workspace_id=workspace.id,
            cluster_domain=cluster_domain,
        )

        async_task(
            "apps.workspaces.tasks.async_add_admins_to_workspace",
            workspace.id,
            request.user.user_id
        )

    return workspace


def connect_xero(authorization_code, redirect_uri, workspace_id):
    if redirect_uri:
        refresh_token = generate_xero_refresh_token(authorization_code, redirect_uri)
    else:
        refresh_token = generate_xero_refresh_token(authorization_code)
    xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace_id).first()
    tenant_mapping = TenantMapping.objects.filter(workspace_id=workspace_id).first()

    workspace = Workspace.objects.get(pk=workspace_id)

    if not xero_credentials:
        xero_credentials = XeroCredentials.objects.create(
            refresh_token=refresh_token, workspace_id=workspace_id
        )

    else:
        xero_credentials.refresh_token = refresh_token
        xero_credentials.is_expired = False
        xero_credentials.save()

    patch_integration_settings(workspace_id, is_token_expired=False)

    if tenant_mapping and not tenant_mapping.connection_id:
        xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)
        connections = xero_connector.connection.connections.get_all()
        connection = list(
            filter(
                lambda connection: connection['tenantId'] == tenant_mapping.tenant_id,
                connections,
            )
        )

        if connection:
            tenant_mapping.connection_id = connection[0]['id']
            tenant_mapping.save()

    if tenant_mapping:
        try:
            xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)
            company_info = xero_connector.get_organisations()[0]
            workspace.xero_currency = company_info['BaseCurrency']
            workspace.save()
            xero_credentials.country = company_info['CountryCode']
            xero_credentials.save()
        except (
            xero_exc.WrongParamsError,
            xero_exc.UnsuccessfulAuthentication,
        ) as exception:
            invalidate_xero_credentials(workspace_id)
            logger.info(exception.response)

    if workspace.onboarding_state == 'CONNECTION':
        workspace.onboarding_state = 'TENANT_MAPPING'
        workspace.save()

    return xero_credentials


def revoke_connections(workspace_id):
    xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace_id).first()
    tenant_mapping = TenantMapping.objects.filter(workspace_id=workspace_id).first()
    if xero_credentials:
        if tenant_mapping and tenant_mapping.connection_id:
            try:
                xero_connector = XeroConnector(
                    xero_credentials, workspace_id=workspace_id
                )
                xero_connector.connection.connections.remove_connection(
                    tenant_mapping.connection_id
                )
            except (
                xero_exc.InvalidGrant,
                xero_exc.UnsupportedGrantType,
                xero_exc.InvalidTokenError,
                xero_exc.UnsuccessfulAuthentication,
                xero_exc.WrongParamsError,
                xero_exc.NoPrivilegeError,
                xero_exc.InternalServerError,
            ):
                pass

        xero_credentials.refresh_token = None
        xero_credentials.country = None
        xero_credentials.is_expired = False
        xero_credentials.save()

        post_delete_xero_connection(workspace_id)


def get_workspace_admin(workspace_id):
    workspace = Workspace.objects.get(pk=workspace_id)
    User = get_user_model()

    admin_email = []
    users = workspace.user.all()
    for user in users:
        admin = User.objects.get(user_id=user)
        employee = ExpenseAttribute.objects.filter(
            value=admin.email, workspace_id=workspace_id, attribute_type="EMPLOYEE"
        ).first()
        if employee:
            admin_email.append(
                {"name": employee.detail["full_name"], "email": admin.email}
            )
    return admin_email


def export_to_xero(workspace_id, expense_group_ids=[], is_direct_export:bool = False, triggered_by: ExpenseImportSourceEnum = None):
    active_xero_credentials = XeroCredentials.objects.filter(
        workspace_id=workspace_id,
        is_expired=False,
        refresh_token__isnull=False
    ).first()

    if not active_xero_credentials:
        if is_direct_export:
            failed_expense_ids = []
            for index, expense_group_id in enumerate(expense_group_ids):
                expense_group = ExpenseGroup.objects.get(id=expense_group_id)
                if index == 0:
                    first_expense = expense_group.expenses.first()
                    update_expenses_in_progress([first_expense])
                    post_accounting_export_summary(workspace_id=workspace_id, expense_ids=[first_expense.id])
                update_failed_expenses(expense_group.expenses.all(), False, True)
                failed_expense_ids.extend(expense_group.expenses.values_list('id', flat=True))
            post_accounting_export_summary(workspace_id=workspace_id, expense_ids=failed_expense_ids, is_failed=True)
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    workspace_schedule = WorkspaceSchedule.objects.filter(workspace_id=workspace_id, interval_hours__gt=0, enabled=True).first()

    last_exported_at = datetime.now()
    is_expenses_exported = False
    export_mode = 'MANUAL' if triggered_by in (ExpenseImportSourceEnum.DASHBOARD_SYNC, ExpenseImportSourceEnum.DIRECT_EXPORT, ExpenseImportSourceEnum.CONFIGURATION_UPDATE) else 'AUTO'
    expense_group_filters = {
        'exported_at__isnull': True,
        'workspace_id': workspace_id
    }
    if expense_group_ids:
        expense_group_filters['id__in'] = expense_group_ids

    if general_settings.reimbursable_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(
            fund_source=FundSourceEnum.PERSONAL,
            **expense_group_filters
        ).values_list("id", flat=True)

        if len(expense_group_ids):
            is_expenses_exported = True

        schedule_bills_creation(
            workspace_id=workspace_id,
            expense_group_ids=expense_group_ids,
            is_auto_export=export_mode == 'AUTO',
            interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0,
            triggered_by=triggered_by
        )

    if general_settings.corporate_credit_card_expenses_object:
        expense_group_ids = ExpenseGroup.objects.filter(
            fund_source=FundSourceEnum.CCC,
            **expense_group_filters
        ).values_list("id", flat=True)

        if len(expense_group_ids):
            is_expenses_exported = True

        schedule_bank_transaction_creation(
            workspace_id=workspace_id,
            expense_group_ids=expense_group_ids,
            is_auto_export=export_mode == 'AUTO',
            interval_hours=workspace_schedule.interval_hours if workspace_schedule else 0,
            triggered_by=triggered_by
        )

    if is_expenses_exported:
        last_export_detail.last_exported_at = last_exported_at
        last_export_detail.export_mode = export_mode or 'MANUAL'

        if workspace_schedule:
            last_export_detail.next_export_at = last_exported_at + timedelta(hours=workspace_schedule.interval_hours)

        last_export_detail.save()
