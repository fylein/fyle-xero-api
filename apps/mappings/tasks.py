import logging
from typing import List

from django_q.tasks import Chain
from fyle_accounting_mappings.models import Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.enums import FyleAttributeEnum
from apps.mappings.exceptions import handle_import_exceptions
from apps.tasks.models import Error
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.utils import XeroConnector

logger = logging.getLogger(__name__)
logger.level = logging.INFO

DEFAULT_FYLE_CATEGORIES = [
    "Activity",
    "Train",
    "Fuel",
    "Snacks",
    "Office Supplies",
    "Utility",
    "Entertainment",
    "Others",
    "Mileage",
    "Food",
    "Per Diem",
    "Bus",
    "Internet",
    "Taxi",
    "Courier",
    "Hotel",
    "Professional Services",
    "Phone",
    "Office Party",
    "Flight",
    "Software",
    "Parking",
    "Toll Charge",
    "Tax",
    "Training",
    "Unspecified",
]


def resolve_expense_attribute_errors(
    source_attribute_type: str,
    workspace_id: int,
    destination_attribute_type: str = None,
):
    """
    Resolve Expense Attribute Errors
    :return: None
    """
    errored_attribute_ids: List[int] = Error.objects.filter(
        is_resolved=False,
        workspace_id=workspace_id,
        type="{}_MAPPING".format(source_attribute_type),
    ).values_list("expense_attribute_id", flat=True)

    if errored_attribute_ids:
        mapped_attribute_ids = []

        mapped_attribute_ids: List[int] = Mapping.objects.filter(
            source_id__in=errored_attribute_ids
        ).values_list("source_id", flat=True)

        if mapped_attribute_ids:
            Error.objects.filter(expense_attribute_id__in=mapped_attribute_ids).update(
                is_resolved=True
            )


@handle_import_exceptions(task_name="async auto map employees")
def async_auto_map_employees(workspace_id: int):
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    employee_mapping_preference = general_settings.auto_map_employees
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id=workspace_id)

    platform.employees.sync()
    xero_connection.sync_contacts()

    Mapping.auto_map_employees("CONTACT", employee_mapping_preference, workspace_id)

    resolve_expense_attribute_errors(
        source_attribute_type=FyleAttributeEnum.EMPLOYEE, workspace_id=workspace_id
    )


def auto_create_suppliers_as_merchants(workspace_id):
    fyle_credentials: FyleCredential = FyleCredential.objects.get(
        workspace_id=workspace_id
    )
    fyle_connection = PlatformConnector(fyle_credentials)

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id=workspace_id)

    merchant_names = xero_connection.get_suppliers()

    if merchant_names:
        fyle_connection.merchants.post(merchant_names, skip_existing_merchants=True)


def auto_import_and_map_fyle_fields(workspace_id):
    """
    Auto import and map fyle fields
    """
    workspace_general_settings: WorkspaceGeneralSettings = (
        WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    )

    chain = Chain()

    if workspace_general_settings.import_suppliers_as_merchants:
        chain.append(
            "apps.mappings.tasks.auto_create_suppliers_as_merchants", workspace_id,
            q_options={
                'cluster': 'import'
            }
        )

    if chain.length() > 0:
        chain.run()
