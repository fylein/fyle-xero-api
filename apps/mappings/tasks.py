import logging
import traceback
from datetime import datetime

from typing import List, Dict

from django_q.models import Schedule

from apps.fyle.utils import FyleConnector
from apps.xero.utils import XeroConnector
from apps.workspaces.models import XeroCredentials, FyleCredential, WorkspaceGeneralSettings
from fyle_accounting_mappings.models import Mapping, MappingSetting, DestinationAttribute, ExpenseAttribute
from fylesdk import WrongParamsError

logger = logging.getLogger(__name__)


def remove_duplicates(xero_attributes: List[DestinationAttribute]):
    unique_attributes = []

    attribute_values = []

    for attribute in xero_attributes:
        if attribute.value not in attribute_values:
            unique_attributes.append(attribute)
            attribute_values.append(attribute.value)

    return unique_attributes


def create_fyle_categories_payload(categories: List[DestinationAttribute], workspace_id: int):
    """
    Create Fyle Categories Payload from Xero Categories
    :param workspace_id: Workspace integer id
    :param categories: Xero Categories
    :return: Fyle Categories Payload
    """
    payload = []

    existing_category_names = ExpenseAttribute.objects.filter(
        attribute_type='CATEGORY', workspace_id=workspace_id).values_list('value', flat=True)

    for category in categories:
        if category.value not in existing_category_names:
            payload.append({
                'name': category.value,
                'code': category.destination_id,
                'enabled': True
            })

    return payload


def upload_categories_to_fyle(workspace_id):
    """
    Upload categories to Fyle
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)
        xero_credentials: XeroCredentials = XeroCredentials.objects.get(workspace_id=workspace_id)

        fyle_connection = FyleConnector(
            refresh_token=fyle_credentials.refresh_token,
            workspace_id=workspace_id
        )

        xero_connection = XeroConnector(
            credentials_object=xero_credentials,
            workspace_id=workspace_id
        )
        fyle_connection.sync_categories(False)
        xero_connection.sync_accounts()

        xero_attributes = DestinationAttribute.objects.filter(attribute_type='ACCOUNT', workspace_id=workspace_id)

        xero_attributes = remove_duplicates(xero_attributes)

        fyle_payload: List[Dict] = create_fyle_categories_payload(xero_attributes, workspace_id)

        if fyle_payload:
            fyle_connection.connection.Categories.post(fyle_payload)
            fyle_connection.sync_categories(False)

        return xero_attributes
        
    except XeroCredentials.DoesNotExist:
        logger.error(
            'Xero Credentials not found for workspace_id %s',
            workspace_id,
        )


def auto_create_category_mappings(workspace_id):
    """
    Create Category Mappings
    :return: mappings
    """

    try:
        fyle_categories = upload_categories_to_fyle(workspace_id=workspace_id)

        Mapping.bulk_create_mappings(fyle_categories, 'CATEGORY', 'ACCOUNT', workspace_id)

        return []

    except WrongParamsError as exception:
        logger.error(
            'Error while creating categories workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.error(
            'Error while creating categories workspace_id - %s error: %s',
            workspace_id, error
        )


def schedule_categories_creation(import_categories, workspace_id):
    if import_categories:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_category_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_category_mappings',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def async_auto_map_employees(workspace_id: int):
    employee_mapping_preference = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id).auto_map_employees

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_connection = FyleConnector(refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id=workspace_id)

    fyle_connection.sync_employees()
    xero_connection.sync_contacts()

    Mapping.auto_map_employees('CONTACT', employee_mapping_preference, workspace_id)


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: str):
    if employee_mapping_preference:
        Schedule.objects.update_or_create(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_map_employees',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()
