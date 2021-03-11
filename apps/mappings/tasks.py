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


def auto_create_category_mappings(workspace_id):
    """
    Create Category Mappings
    :return: mappings
    """
    category_mappings = []

    try:
        fyle_categories = upload_categories_to_fyle(workspace_id=workspace_id)

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

                mapping.source.auto_mapped = True
                mapping.source.auto_created = True
                mapping.source.save(update_fields=['auto_mapped', 'auto_created'])

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


def filter_expense_attributes(workspace_id: int, **filters):
    return ExpenseAttribute.objects.filter(attribute_type='EMPLOYEE', workspace_id=workspace_id, **filters).all()


def auto_create_employee_mappings(source_attributes: List[ExpenseAttribute], mapping_attributes: dict):
    for source in source_attributes:
        mapping = Mapping.objects.filter(
            source_type='EMPLOYEE',
            destination_type=mapping_attributes['destination_type'],
            source__value=source.value,
            workspace_id=mapping_attributes['workspace_id']
        ).first()

        if not mapping:
            Mapping.create_or_update_mapping(
                source_type='EMPLOYEE',
                destination_type=mapping_attributes['destination_type'],
                source_value=source.value,
                destination_value=mapping_attributes['destination_value'],
                destination_id=mapping_attributes['destination_id'],
                workspace_id=mapping_attributes['workspace_id']
            )

            source.auto_mapped = True
            source.save(update_fields=['auto_mapped'])


def construct_filters_employee_mappings(employee: DestinationAttribute, employee_mapping_preference: str):
    filters = {}
    if employee_mapping_preference == 'EMAIL':
        if employee.detail and employee.detail['email']:
            filters = {
                'value__iexact': employee.detail['email']
            }

    elif employee_mapping_preference == 'NAME':
        filters = {
            'detail__full_name__iexact': employee.value
        }

    elif employee_mapping_preference == 'EMPLOYEE_CODE':
        filters = {
            'detail__employee_code__iexact': employee.value
        }

    return filters


def async_auto_map_employees(workspace_id):
    employee_mapping_preference = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id).auto_map_employees
    source_attributes = []
    employee_attributes = DestinationAttribute.objects.filter(attribute_type='CONTACT',
                                                              workspace_id=workspace_id)

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_connection = FyleConnector(refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id)

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id=workspace_id)

    fyle_connection.sync_employees()
    xero_connection.sync_contacts()

    for employee in employee_attributes:
        filters = construct_filters_employee_mappings(employee, employee_mapping_preference)

        if filters:
            filters['auto_mapped'] = False
            source_attributes = filter_expense_attributes(workspace_id, **filters)

        mapping_attributes = {
            'destination_type': 'CONTACT',
            'destination_value': employee.value,
            'destination_id': employee.destination_id,
            'workspace_id': workspace_id
        }

        auto_create_employee_mappings(source_attributes, mapping_attributes)


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
