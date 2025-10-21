from datetime import datetime, timezone
from unittest import mock

import pytest
from fyle.platform import Platform
from fyle_rest_auth.models import AuthToken, User
from rest_framework.test import APIClient

from apps.fyle.helpers import get_access_token
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.workspaces.models import LastExportDetail, Workspace, WorkspaceGeneralSettings
from fyle_xero_api.tests import settings
from tests.test_fyle.fixtures import data as fyle_data


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def mock_rabbitmq():
    with mock.patch('apps.fyle.queue.RabbitMQConnection.get_instance') as mock_rabbitmq:
        mock_instance = mock.Mock()
        mock_instance.publish.return_value = None
        mock_instance.connect.return_value = None
        mock_rabbitmq.return_value = mock_instance
        yield mock_rabbitmq


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture(request):
    patched_1 = mock.patch("xerosdk.XeroSDK.refresh_access_token")
    patched_1.__enter__()

    patched_2 = mock.patch(
        "fyle_rest_auth.authentication.get_fyle_admin",
        return_value=fyle_data["get_my_profile"],
    )
    patched_2.__enter__()

    patched_3 = mock.patch(
        "fyle.platform.internals.auth.Auth.update_access_token",
        return_value="asnfalsnkflanskflansfklsan",
    )
    patched_3.__enter__()

    patched_4 = mock.patch(
        "apps.fyle.helpers.post_request",
        return_value={
            "access_token": "easnfkjo12233.asnfaosnfa.absfjoabsfjk",
            "cluster_domain": "https://staging.fyle.tech",
        },
    )
    patched_4.__enter__()

    patched_5 = mock.patch(
        "fyle.platform.apis.v1.spender.MyProfile.get",
        return_value=fyle_data["get_my_profile"],
    )
    patched_5.__enter__()


@pytest.fixture()
def test_connection(db):
    """
    Creates a connection with Fyle
    """
    client_id = settings.FYLE_CLIENT_ID
    client_secret = settings.FYLE_CLIENT_SECRET
    token_url = settings.FYLE_TOKEN_URI
    refresh_token = settings.FYLE_REFRESH_TOKEN
    server_url = settings.FYLE_SERVER_URL

    fyle_connection = Platform(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        server_url=server_url,
    )

    access_token = get_access_token(refresh_token)
    fyle_connection.access_token = access_token
    user_profile = fyle_connection.v1.spender.my_profile.get()["data"]
    user = User(
        password="",
        last_login=datetime.now(tz=timezone.utc),
        id=1,
        email=user_profile["user"]["email"],
        user_id=user_profile["user_id"],
        full_name="",
        active="t",
        staff="f",
        admin="t",
    )

    user.save()

    auth_token = AuthToken(id=1, refresh_token=refresh_token, user=user)
    auth_token.save()

    workspace = Workspace.objects.create(
        name="Test Workspace 2",
        fyle_org_id="fyle_org_id_dummy",
        fyle_currency="USD",
        xero_currency="USD",
        app_version="v2",
        xero_short_code="xero_short_code_dummy",
        onboarding_state="COMPLETE",
    )
    workspace.user.add(user)
    LastExportDetail.objects.create(workspace=workspace)
    WorkspaceGeneralSettings.objects.create(
        workspace=workspace, reimbursable_expenses_object="BILL"
    )
    ExpenseGroupSettings.objects.create(workspace=workspace)

    return fyle_connection


@pytest.fixture
def add_expense_report_data(db):
    """
    Create test data for expense report change tests
    """
    workspace = Workspace.objects.get(id=1)

    # Create test expenses
    expense1 = Expense.objects.create(
        workspace_id=workspace.id,
        expense_id='tx_report_test_1',
        employee_email='test@fyle.in',
        employee_name='Test Employee',
        category='Meals',
        sub_category='Team Meals',
        project='Test Project',
        expense_number='E/2024/01/T/1',
        claim_number='C/2024/01/R/1',
        amount=100.0,
        currency='USD',
        foreign_amount=100.0,
        foreign_currency='USD',
        settlement_id='setl_test_1',
        reimbursable=True,
        billable=False,
        state='APPROVED',
        vendor='Test Vendor',
        cost_center='Test Cost Center',
        purpose='Test meal expense',
        report_id='rp_test_report_1',
        spent_at='2024-01-01T00:00:00Z',
        approved_at='2024-01-01T00:00:00Z',
        expense_created_at='2024-01-01T00:00:00Z',
        expense_updated_at='2024-01-01T00:00:00Z',
        created_at='2024-01-01T00:00:00Z',
        updated_at='2024-01-01T00:00:00Z',
        fund_source='PERSONAL',
        verified_at='2024-01-01T00:00:00Z',
        custom_properties={},
        org_id=workspace.fyle_org_id,
        file_ids=[],
        accounting_export_summary={}
    )

    expense2 = Expense.objects.create(
        workspace_id=workspace.id,
        expense_id='tx_report_test_2',
        employee_email='test@fyle.in',
        employee_name='Test Employee',
        category='Travel',
        sub_category='Flight',
        project='Test Project',
        expense_number='E/2024/01/T/2',
        claim_number='C/2024/01/R/1',
        amount=200.0,
        currency='USD',
        foreign_amount=200.0,
        foreign_currency='USD',
        settlement_id='setl_test_2',
        reimbursable=True,
        billable=False,
        state='APPROVED',
        vendor='Test Airline',
        cost_center='Test Cost Center',
        purpose='Test travel expense',
        report_id='rp_test_report_1',
        spent_at='2024-01-01T00:00:00Z',
        approved_at='2024-01-01T00:00:00Z',
        expense_created_at='2024-01-01T00:00:00Z',
        expense_updated_at='2024-01-01T00:00:00Z',
        created_at='2024-01-01T00:00:00Z',
        updated_at='2024-01-01T00:00:00Z',
        fund_source='PERSONAL',
        verified_at='2024-01-01T00:00:00Z',
        custom_properties={},
        org_id=workspace.fyle_org_id,
        file_ids=[],
        accounting_export_summary={}
    )

    # Create non-exported expense group
    expense_group = ExpenseGroup.objects.create(
        workspace_id=workspace.id,
        fund_source='PERSONAL',
        exported_at=None,
        description={
            'report_id': 'rp_test_report_1',
            'employee_email': 'test@fyle.in',
            'claim_number': 'C/2024/01/R/1',
            'fund_source': 'PERSONAL'
        }
    )
    expense_group.expenses.add(expense1, expense2)

    return {
        'workspace': workspace,
        'expenses': [expense1, expense2],
        'expense_group': expense_group
    }
