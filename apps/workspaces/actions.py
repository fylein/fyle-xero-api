import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django_q.tasks import async_task
from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_rest_auth.helpers import get_fyle_admin
from fyle_rest_auth.models import AuthToken
from xerosdk import exceptions as xero_exc

from apps.fyle.helpers import get_cluster_domain
from apps.fyle.models import ExpenseGroupSettings
from apps.mappings.models import TenantMapping
from apps.workspaces.models import FyleCredential, LastExportDetail, Workspace, XeroCredentials
from apps.workspaces.signals import post_delete_xero_connection
from apps.workspaces.utils import generate_xero_refresh_token
from apps.xero.utils import XeroConnector

logger = logging.getLogger(__name__)


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

        async_task('apps.workspaces.tasks.async_create_admin_subcriptions', workspace.id)

        async_task(
            "apps.workspaces.tasks.async_add_admins_to_workspace",
            workspace.id,
            request.user.user_id,
            q_options={
                'cluster': 'import'
            }
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

    if tenant_mapping and not tenant_mapping.connection_id:
        xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)
        connections = xero_connector.connection.connections.get_all()
        connection = list(
            filter(
                lambda connection: connection["tenantId"] == tenant_mapping.tenant_id,
                connections,
            )
        )

        if connection:
            tenant_mapping.connection_id = connection[0]["id"]
            tenant_mapping.save()

    if tenant_mapping:
        try:
            xero_connector = XeroConnector(xero_credentials, workspace_id=workspace_id)
            company_info = xero_connector.get_organisations()[0]
            workspace.xero_currency = company_info["BaseCurrency"]
            workspace.save()
            xero_credentials.country = company_info["CountryCode"]
            xero_credentials.save()
        except (
            xero_exc.WrongParamsError,
            xero_exc.UnsuccessfulAuthentication,
        ) as exception:
            logger.info(exception.response)

    if workspace.onboarding_state == "CONNECTION":
        workspace.onboarding_state = "EXPORT_SETTINGS"
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
        xero_credentials.is_expired = True
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
