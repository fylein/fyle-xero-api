import logging
from datetime import datetime, timezone
from typing import List

from fyle_accounting_mappings.models import Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.enums import FyleAttributeEnum
from apps.mappings.exceptions import handle_import_exceptions
from apps.tasks.models import Error
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.utils import XeroConnector
from workers.helpers import RoutingKeyEnum, WorkerActionEnum, publish_to_rabbitmq

logger = logging.getLogger(__name__)
logger.level = logging.INFO


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
                is_resolved=True, updated_at=datetime.now(timezone.utc)
            )


def async_auto_map_employees(workspace_id: int) -> None:
    """
    Schedule async auto map employees via RabbitMQ
    :param workspace_id: Workspace Id
    :return: None
    """
    payload = {
        'workspace_id': workspace_id,
        'action': WorkerActionEnum.AUTO_MAP_EMPLOYEES.value,
        'data': {
            'workspace_id': workspace_id
        }
    }
    publish_to_rabbitmq(payload=payload, routing_key=RoutingKeyEnum.IMPORT.value)


@handle_import_exceptions(task_name="async auto map employees")
def trigger_async_auto_map_employees(workspace_id: int):
    """
    Trigger async auto map employees
    :param workspace_id: Workspace Id
    :return: None
    """
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
