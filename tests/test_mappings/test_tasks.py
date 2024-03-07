from unittest import mock

from django_q.models import Schedule
from fyle.platform.exceptions import InternalServerError
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle_accounting_mappings.models import (
    EmployeeMapping,
    ExpenseAttribute,
    Mapping
)
from xerosdk.exceptions import UnsuccessfulAuthentication

from apps.fyle.models import ExpenseGroup
from apps.mappings.queue import (
    schedule_auto_map_employees
)
from apps.mappings.tasks import (
    async_auto_map_employees,
    resolve_expense_attribute_errors
)
from apps.tasks.models import Error
from apps.workspaces.models import WorkspaceGeneralSettings, XeroCredentials
from tests.test_fyle.fixtures import data as fyle_data
from tests.test_xero.fixtures import data as xero_data


def test_async_auto_map_employees(mocker, db):
    workspace_id = 1

    mocker.patch(
        "xerosdk.apis.Contacts.list_all_generator",
        return_value=xero_data["get_all_contacts"],
    )

    mocker.patch(
        "fyle.platform.apis.v1beta.admin.Employees.list_all",
        return_value=fyle_data["get_all_employees"],
    )

    async_auto_map_employees(workspace_id)
    employee_mappings = EmployeeMapping.objects.filter(
        workspace_id=workspace_id
    ).count()
    assert employee_mappings == 0

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.employee_field_mapping = "VENDOR"
    general_settings.save()

    async_auto_map_employees(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(
        workspace_id=workspace_id
    ).count()
    assert employee_mappings == 0

    with mock.patch("fyle.platform.apis.v1beta.admin.Employees.list_all") as mock_call:
        mock_call.side_effect = FyleInvalidTokenError(
            msg="Invalid Token for Fyle", response="Invalid Token for Fyle"
        )
        async_auto_map_employees(workspace_id=workspace_id)

        mock_call.side_effect = UnsuccessfulAuthentication(msg="Auth error")
        async_auto_map_employees(workspace_id=workspace_id)

        mock_call.side_effect = InternalServerError(
            msg="Internal server error while importing to Fyle"
        )
        async_auto_map_employees(workspace_id=workspace_id)

    qbo_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    qbo_credentials.delete()

    async_auto_map_employees(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(
        workspace_id=workspace_id
    ).count()
    assert employee_mappings == 0


def test_schedule_auto_map_employees(db):
    workspace_id = 1

    schedule_auto_map_employees(
        employee_mapping_preference=True, workspace_id=workspace_id
    )

    schedule = Schedule.objects.filter(
        func="apps.mappings.tasks.async_auto_map_employees",
        args="{}".format(workspace_id),
    ).first()

    assert schedule.func == "apps.mappings.tasks.async_auto_map_employees"

    schedule_auto_map_employees(
        employee_mapping_preference=False, workspace_id=workspace_id
    )

    schedule = Schedule.objects.filter(
        func="apps.mappings.tasks.async_auto_map_employees",
        args="{}".format(workspace_id),
    ).first()

    assert schedule == None


def test_resolve_expense_attribute_errors(db):
    workspace_id = 1
    expense_group = ExpenseGroup.objects.get(id=3)

    employee_attribute = ExpenseAttribute.objects.filter(
        value=expense_group.description.get("employee_email"),
        workspace_id=expense_group.workspace_id,
        attribute_type="EMPLOYEE",
    ).first()

    Mapping.objects.get(
        destination_type="CONTACT",
        source_type="EMPLOYEE",
        source=employee_attribute,
        workspace_id=expense_group.workspace_id,
    )

    error, _ = Error.objects.update_or_create(
        workspace_id=expense_group.workspace_id,
        expense_attribute=employee_attribute,
        defaults={
            "type": "EMPLOYEE_MAPPING",
            "error_title": employee_attribute.value,
            "error_detail": "Employee mapping is missing",
            "is_resolved": False,
        },
    )

    resolve_expense_attribute_errors("EMPLOYEE", workspace_id, "CONTACT")
    assert Error.objects.get(id=error.id).is_resolved == True
