import logging
import traceback
from datetime import datetime, timedelta

from typing import List, Dict

from django_q.models import Schedule

from fyle_integrations_platform_connector import PlatformConnector

from fyle_accounting_mappings.models import Mapping, MappingSetting, DestinationAttribute, ExpenseAttribute

from fyle.platform.exceptions import WrongParamsError

from apps.xero.utils import XeroConnector
from apps.workspaces.models import XeroCredentials, FyleCredential, WorkspaceGeneralSettings
from .constants import FYLE_EXPENSE_SYSTEM_FIELDS

logger = logging.getLogger(__name__)
logger.level = logging.INFO

DEFAULT_FYLE_CATEGORIES = [
    'Activity', 'Train', 'Fuel', 'Snacks', 'Office Supplies', 'Utility', 'Entertainment', 'Others', 'Mileage', 'Food',
    'Per Diem', 'Bus', 'Internet', 'Taxi', 'Courier', 'Hotel', 'Professional Services', 'Phone', 'Office Party',
    'Flight', 'Software', 'Parking', 'Toll Charge', 'Tax', 'Training', 'Unspecified'
]


def remove_duplicates(xero_attributes: List[DestinationAttribute]):
    unique_attributes = []

    attribute_values = []

    for attribute in xero_attributes:
        if attribute.value not in attribute_values:
            unique_attributes.append(attribute)
            attribute_values.append(attribute.value)

    return unique_attributes


def create_fyle_categories_payload(categories: List[DestinationAttribute], workspace_id: int, category_map: Dict):
    """
    Create Fyle Categories Payload from Xero Categories
    :param workspace_id: Workspace integer id
    :param categories: Xero Categories
    :return: Fyle Categories Payload
    """
    payload = []

    for category in categories:
        # Xero account active and is not present in Fyle -> New category will be created
        if category.value.lower() not in category_map and category.active:
            payload.append({
                'name': category.value,
                'code': category.destination_id,
                'is_enabled': category.active,
                'restricted_project_ids': None
            })
        # Xero Account is not active and present in Fyle -> This category will be disabled now
        elif not category.active and category.value.lower() in category_map:
            payload.append({
                'id': category_map[category.value.lower()]['id'],
                'name': category.value,
                'code': category.destination_id,
                'is_enabled': category.active,
                'restricted_project_ids': None
            })
        # Xero Account is active and already present in Fyle -> This category will be enabled now
        elif category.active and category.value.lower() in category_map:
            payload.append({
                'id': category_map[category.value.lower()]['id'],
                'name': category.value,
                'code': category.destination_id,
                'is_enabled': category.active,
                'restricted_project_ids': None
            })
    return payload


def get_all_categories_from_fyle(platform: PlatformConnector):
    categories_generator = platform.connection.v1beta.admin.categories.list_all(query_params={
        'order': 'id.desc'
    })
    categories = []

    for response in categories_generator:
        if response.get('data'):
            categories.extend(response['data'])

    category_name_map = {}
    for category in categories:
        if category['sub_category'] and category['name'] != category['sub_category']:
            category['name'] = '{0} / {1}'.format(category['name'], category['sub_category'])
        category_name_map[category['name'].lower()] = category

    return category_name_map


def disable_inactive_expense_attributes(source_field, destination_field, workspace_id):
    # Get All the inactive destination attribute ids
    destination_attribute_ids = DestinationAttribute.objects.filter(
        attribute_type=destination_field,
        mapping__isnull=False,
        mapping__destination_type=destination_field,
        active=False,
        workspace_id=workspace_id
    ).values_list('id', flat=True)

    # Get all the expense attributes that are mapped to these destination_attribute_ids
    expense_attributes = ExpenseAttribute.objects.filter(
        attribute_type=source_field,
        mapping__destination_id__in=destination_attribute_ids,
        active=True
    )

    # if there are any expense attributes present, set active to False
    if expense_attributes:
        expense_attributes_ids = [expense_attribute.id for expense_attribute in expense_attributes]
        expense_attributes.update(active=False)
        return expense_attributes_ids


def upload_categories_to_fyle(workspace_id):
    """
    Upload categories to Fyle
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)
        xero_credentials: XeroCredentials = XeroCredentials.objects.get(workspace_id=workspace_id)
        general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
        platform = PlatformConnector(fyle_credentials)

        category_map = get_all_categories_from_fyle(platform=platform)

        xero_connection = XeroConnector(
            credentials_object=xero_credentials,
            workspace_id=workspace_id
        )
        platform.categories.sync()
        xero_connection.sync_accounts()

        xero_attributes = DestinationAttribute.objects.filter(
            workspace_id=workspace_id,
            attribute_type='ACCOUNT',
            detail__account_type__in=general_settings.charts_of_accounts
        ).all()

        xero_attributes = remove_duplicates(xero_attributes)

        fyle_payload: List[Dict] = create_fyle_categories_payload(xero_attributes, workspace_id, category_map)

        if fyle_payload:
            platform.categories.post_bulk(fyle_payload)
            platform.categories.sync()
            disable_inactive_expense_attributes('CATEGORY', 'ACCOUNT', workspace_id)

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
        logger.exception(
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
    try:
        employee_mapping_preference = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id).auto_map_employees

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)

        xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
        xero_connection = XeroConnector(xero_credentials, workspace_id=workspace_id)

        platform.employees.sync()
        xero_connection.sync_contacts()

        Mapping.auto_map_employees('CONTACT', employee_mapping_preference, workspace_id)

    except XeroCredentials.DoesNotExist:
        logger.error(
            'Xero Credentials not found for workspace_id %s',
            workspace_id,
        )


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


def sync_xero_attributes(xero_attribute_type: str, workspace_id: int):
    xero_credentials: XeroCredentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(
        credentials_object=xero_credentials,
        workspace_id=workspace_id
    )

    if xero_attribute_type == 'ITEM':
        xero_connection.sync_items()
    elif xero_attribute_type == 'TAX_CODE':
        xero_connection.sync_tax_codes()
    else:
        xero_connection.sync_tracking_categories()


def create_fyle_cost_centers_payload(xero_attributes: List[DestinationAttribute], existing_fyle_cost_centers: list):
    """
    Create Fyle Cost Centers Payload from xero Objects
    :param workspace_id: Workspace integer id
    :param xero_attributes: xero Objects
    :param fyle_attribute: Fyle Attribute
    :return: Fyle Cost Centers Payload
    """

    fyle_cost_centers_payload = []

    for xero_attribute in xero_attributes:
        if xero_attribute.value not in existing_fyle_cost_centers:
            fyle_cost_centers_payload.append({
                'name': xero_attribute.value,
                'is_enabled': True if xero_attribute.active is None else xero_attribute.active,
                'description': 'Cost Center - {0}, Id - {1}'.format(
                    xero_attribute.value,
                    xero_attribute.destination_id
                )
            })
    return fyle_cost_centers_payload


def post_cost_centers_in_batches(platform: PlatformConnector, workspace_id: int, xero_attribute_type: str):
    existing_cost_center_names = ExpenseAttribute.objects.filter(
        attribute_type='COST_CENTER', workspace_id=workspace_id).values_list('value', flat=True)

    xero_attribute_count = DestinationAttribute.objects.filter(
        attribute_type=xero_attribute_type, workspace_id=workspace_id).count()

    page_size = 200

    for offset in range(0, xero_attribute_count, page_size):
        limit = offset + page_size
        paginated_xero_attributes = DestinationAttribute.objects.filter(
            attribute_type=xero_attribute_type, workspace_id=workspace_id
        ).order_by('value', 'id')[offset:limit]

        paginated_xero_attributes = remove_duplicates(paginated_xero_attributes)

        fyle_payload: List[Dict] = create_fyle_cost_centers_payload(
            paginated_xero_attributes, existing_cost_center_names)

        if fyle_payload:
            platform.cost_centers.post_bulk(fyle_payload)
            platform.cost_centers.sync()

        Mapping.bulk_create_mappings(paginated_xero_attributes, 'COST_CENTER', xero_attribute_type, workspace_id)


def auto_create_cost_center_mappings(workspace_id: int):
    """
    Create Cost Center Mappings
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials)

        mapping_setting = MappingSetting.objects.get(
            source_field='COST_CENTER', import_to_fyle=True, workspace_id=workspace_id
        )

        platform.cost_centers.sync()

        sync_xero_attributes(mapping_setting.destination_field, workspace_id=workspace_id)

        post_cost_centers_in_batches(platform, workspace_id, mapping_setting.destination_field)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating cost centers workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while creating cost centers workspace_id - %s error: %s',
            workspace_id, error
        )


def schedule_cost_centers_creation(import_to_fyle, workspace_id: int):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_cost_center_mappings',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def create_fyle_projects_payload(projects: List[DestinationAttribute], existing_project_names: list):
    """
    Create Fyle Projects Payload from Xero Projects and Customers
    :param projects: Xero Projects
    :return: Fyle Projects Payload
    """
    payload = []

    for project in projects:
        if project.value not in existing_project_names:
            payload.append({
                'name': project.value,
                'code': project.destination_id,
                'description': 'Project - {0}, Id - {1}'.format(
                    project.value,
                    project.destination_id
                ),
                'is_enabled': True if project.active is None else project.active
            })

    return payload


def post_projects_in_batches(platform: PlatformConnector,
                             workspace_id: int, destination_field: str):
    existing_project_names = ExpenseAttribute.objects.filter(
        attribute_type='PROJECT', workspace_id=workspace_id).values_list('value', flat=True)
    xero_attributes_count = DestinationAttribute.objects.filter(
        attribute_type=destination_field, workspace_id=workspace_id).count()
    page_size = 200

    for offset in range(0, xero_attributes_count, page_size):
        limit = offset + page_size
        paginated_xero_attributes = DestinationAttribute.objects.filter(
            attribute_type=destination_field, workspace_id=workspace_id).order_by('value', 'id')[offset:limit]

        paginated_xero_attributes = remove_duplicates(paginated_xero_attributes)

        fyle_payload: List[Dict] = create_fyle_projects_payload(
            paginated_xero_attributes, existing_project_names)

        if fyle_payload:
            platform.projects.post_bulk(fyle_payload)
            platform.projects.sync()

        Mapping.bulk_create_mappings(paginated_xero_attributes, 'PROJECT', destination_field, workspace_id)


def auto_create_project_mappings(workspace_id: int):
    """
    Create Project Mappings
    :return: mappings
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials)

        platform.projects.sync()

        mapping_setting = MappingSetting.objects.get(
            source_field='PROJECT', workspace_id=workspace_id
        )

        sync_xero_attributes(mapping_setting.destination_field, workspace_id)

        post_projects_in_batches(platform, workspace_id, mapping_setting.destination_field)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating projects workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while creating projects workspace_id - %s error: %s',
            workspace_id, error
        )


def schedule_projects_creation(import_to_fyle, workspace_id):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_project_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_project_mappings',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def create_fyle_expense_custom_fields_payload(xero_attributes: List[DestinationAttribute], workspace_id: int,
                                              fyle_attribute: str, platform: PlatformConnector):
    """
    Create Fyle Expense Custom Field Payload from Xero Objects
    :param workspace_id: Workspace ID
    :param xero_attributes: Xero Objects
    :param fyle_attribute: Fyle Attribute
    :return: Fyle Expense Custom Field Payload
    """

    fyle_expense_custom_field_options = []

    [fyle_expense_custom_field_options.append(xero_attribute.value) for xero_attribute in xero_attributes]

    if fyle_attribute.lower() not in FYLE_EXPENSE_SYSTEM_FIELDS:
        existing_attribute = ExpenseAttribute.objects.filter(
            attribute_type=fyle_attribute, workspace_id=workspace_id).values_list('detail', flat=True).first()

        custom_field_id = None
        if existing_attribute is not None:
            custom_field_id = existing_attribute['custom_field_id']

        fyle_attribute = fyle_attribute.replace('_', ' ').title()

        expense_custom_field_payload = {
            'field_name': fyle_attribute,
            'type': 'SELECT',
            'is_enabled': True,
            'is_mandatory': False,
            'placeholder': 'Select {0}'.format(fyle_attribute),
            'options': fyle_expense_custom_field_options,
            'code': None
        }

        if custom_field_id:
            expense_field = platform.expense_custom_fields.get_by_id(custom_field_id)
            expense_custom_field_payload['id'] = custom_field_id
            expense_custom_field_payload['is_mandatory'] = expense_field['is_mandatory']

        return expense_custom_field_payload


def upload_attributes_to_fyle(workspace_id: int, xero_attribute_type: str, fyle_attribute_type: str):
    """
    Upload attributes to Fyle
    """
    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentials)

    xero_attributes: List[DestinationAttribute] = DestinationAttribute.objects.filter(
        workspace_id=workspace_id, attribute_type=xero_attribute_type
    )

    xero_attributes = remove_duplicates(xero_attributes)

    fyle_custom_field_payload = create_fyle_expense_custom_fields_payload(
        xero_attributes=xero_attributes,
        workspace_id=workspace_id,
        fyle_attribute=fyle_attribute_type,
        platform=platform
    )

    if fyle_custom_field_payload:
        platform.expense_custom_fields.post(fyle_custom_field_payload)
        platform.expense_custom_fields.sync()

    return xero_attributes


def auto_create_expense_fields_mappings(workspace_id: int, xero_attribute_type: str, fyle_attribute_type: str):
    """
    Create Fyle Attributes Mappings
    :return: mappings
    """
    try:
        fyle_attributes = upload_attributes_to_fyle(workspace_id=workspace_id, xero_attribute_type=xero_attribute_type,
                                                    fyle_attribute_type=fyle_attribute_type)
        if fyle_attributes:
            Mapping.bulk_create_mappings(fyle_attributes, fyle_attribute_type, xero_attribute_type, workspace_id)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating %s workspace_id - %s in Fyle %s %s',
            fyle_attribute_type, workspace_id, exception.message, {'error': exception.response}
        )
    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.exception(
            'Error while creating %s workspace_id - %s error: %s', fyle_attribute_type, workspace_id, error
        )


def async_auto_create_custom_field_mappings(workspace_id: str):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()

    for mapping_setting in mapping_settings:
        if mapping_setting.import_to_fyle:
            sync_xero_attributes(mapping_setting.destination_field, workspace_id)
            auto_create_expense_fields_mappings(
                workspace_id, mapping_setting.destination_field, mapping_setting.source_field
            )


def schedule_fyle_attributes_creation(workspace_id: int):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()

    if mapping_settings:
        schedule, _ = Schedule.objects.get_or_create(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args='{0}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now() + timedelta(hours=24)
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
            args=workspace_id
        ).first()

        if schedule:
            schedule.delete()


def upload_tax_groups_to_fyle(platform_connection: PlatformConnector, workspace_id: int):
    existing_tax_codes_name = ExpenseAttribute.objects.filter(
        attribute_type='TAX_GROUP', workspace_id=workspace_id).values_list('value', flat=True)

    xero_attributes = DestinationAttribute.objects.filter(
        attribute_type='TAX_CODE', workspace_id=workspace_id).order_by('value', 'id')

    xero_attributes = remove_duplicates(xero_attributes)

    fyle_payload: List[Dict] = create_fyle_tax_group_payload(xero_attributes, existing_tax_codes_name)

    if fyle_payload:
        platform_connection.tax_groups.post_bulk(fyle_payload)

    platform_connection.tax_groups.sync()
    Mapping.bulk_create_mappings(xero_attributes, 'TAX_GROUP', 'TAX_CODE', workspace_id)


def create_fyle_tax_group_payload(xero_attributes: List[DestinationAttribute], existing_fyle_tax_groups: list):
    """
    Create Fyle tax Group Payload from Xero Objects
    :param existing_fyle_tax_groups: Existing tax groups names
    :param xero_attributes: Xero Objects
    :return: Fyle tax Group Payload
    """

    fyle_tax_group_payload = []
    for xero_attribute in xero_attributes:
        if xero_attribute.value not in existing_fyle_tax_groups:
            fyle_tax_group_payload.append(
                {
                    'name': xero_attribute.value,
                    'is_enabled': True,
                    'percentage': round((xero_attribute.detail['tax_rate'] / 100), 2)
                }
            )

    return fyle_tax_group_payload


def auto_create_tax_codes_mappings(workspace_id: int):
    """
    Create Tax Codes Mappings
    :return: None
    """
    try:
        fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials=fyle_credentials)
        platform.tax_groups.sync()

        sync_xero_attributes('TAX_CODE', workspace_id)

        upload_tax_groups_to_fyle(platform, workspace_id)

    except WrongParamsError as exception:
        logger.error(
            'Error while creating tax groups workspace_id - %s in Fyle %s %s',
            workspace_id, exception.message, {'error': exception.response}
        )

    except Exception:
        error = traceback.format_exc()
        error = {
            'error': error
        }
        logger.error(
            'Error while creating tax groups workspace_id - %s error: %s',
            workspace_id, error
        )


def schedule_tax_groups_creation(import_tax_codes, workspace_id):
    if import_tax_codes:
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.mappings.tasks.auto_create_tax_codes_mappings',
            args='{}'.format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()
