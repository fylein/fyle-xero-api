import logging
import traceback
from datetime import datetime

from typing import List, Dict

from django_q.models import Schedule

from apps.fyle.utils import FyleConnector
from apps.xero.utils import XeroConnector
from apps.workspaces.models import XeroCredentials, FyleCredential
from fyle_accounting_mappings.models import MappingSetting, Mapping, DestinationAttribute, ExpenseAttribute
from fylesdk import WrongParamsError

logger = logging.getLogger(__name__)


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
                'code': 'Xero - ' + category.destination_id,
                'enabled': True
            })

    return payload


def upload_categories_to_fyle(workspace_id):
    """
    Upload categories to Fyle
    """
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

    xero_attributes = DestinationAttribute.objects.filter(
        attribute_type='ACCOUNT', workspace_id=workspace_id)

    fyle_payload: List[Dict] = create_fyle_categories_payload(xero_attributes, workspace_id)

    if fyle_payload:
        fyle_connection.connection.Categories.post(fyle_payload)
        fyle_connection.sync_categories(False)

    return xero_attributes


def auto_create_category_mappings(workspace_id):
    """
    Create Category Mappings
    :return: mappings
    """
    MappingSetting.bulk_upsert_mapping_setting([{
        'source_field': 'CATEGORY',
        'destination_field': 'ACCOUNT'
    }], workspace_id=workspace_id)

    fyle_categories = upload_categories_to_fyle(workspace_id=workspace_id)

    category_mappings = []

    try:
        for category in fyle_categories:
            try:
                mapping = Mapping.create_or_update_mapping(
                    source_type='CATEGORY',
                    destination_type='ACCOUNT',
                    source_value=category.value,
                    destination_value=category.value,
                    destination_id=category.destination_id,
                    workspace_id=workspace_id
                )
                category_mappings.append(mapping)

            except ExpenseAttribute.DoesNotExist:
                detail = {
                    'source_value': category.value,
                    'destination_value': category.value
                }
                logger.error(
                    'Error while creating categories auto mapping workspace_id - %s %s',
                    workspace_id, {'payload': detail}
                )
                raise ExpenseAttribute.DoesNotExist

        return category_mappings

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
