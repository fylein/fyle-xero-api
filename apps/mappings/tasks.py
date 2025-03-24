import logging
from typing import List
from datetime import datetime, timedelta, timezone

from fyle_accounting_mappings.models import Mapping
from fyle_integrations_platform_connector import PlatformConnector

from apps.fyle.enums import FyleAttributeEnum
from apps.mappings.exceptions import handle_import_exceptions
from apps.tasks.models import Error
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.utils import XeroConnector
from fyle_integrations_imports.models import ImportLog

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
    logger.info("| Importing Suppliers as Merchant to Fyle | Content: {{WORKSPACE_ID: {}}}".format(workspace_id))

    import_log, is_created = ImportLog.objects.get_or_create(
        workspace_id=workspace_id,
        attribute_type="MERCHANT",
        defaults={
            'status': 'IN_PROGRESS'
        }
    )

    sync_after = None

    if not is_created:
        sync_after = import_log.last_successful_run_at if import_log.last_successful_run_at else None

    time_difference = datetime.now() - timedelta(minutes=30)
    offset_aware_time_difference = time_difference.replace(tzinfo=timezone.utc)

    if (import_log.status == 'IN_PROGRESS' and not is_created) \
        or (sync_after and (sync_after > offset_aware_time_difference)):
        return

    else:
        import_log.status = 'IN_PROGRESS'
        import_log.processed_batches_count = 0
        import_log.total_batches_count = 0
        import_log.save()

    fyle_credentials: FyleCredential = FyleCredential.objects.get(
        workspace_id=workspace_id
    )
    fyle_connection = PlatformConnector(fyle_credentials)

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id=workspace_id)

    merchant_names = xero_connection.get_suppliers()

    if merchant_names:
        fyle_connection.merchants.post(merchant_names, skip_existing_merchants=True)

    import_log.status = 'COMPLETE'
    import_log.last_successful_run_at = datetime.now()
    import_log.error_log = []
    import_log.total_batches_count = 0
    import_log.processed_batches_count = 0
    import_log.save()
