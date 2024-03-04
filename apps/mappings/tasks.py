import logging
from typing import Dict, List

from django_q.tasks import Chain
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping
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


def disable_expense_attributes(source_field, destination_field, workspace_id):
    filter = {"mapping__isnull": False, "mapping__destination_type": destination_field}

    destination_attribute_ids = DestinationAttribute.objects.filter(
        attribute_type=destination_field,
        active=False,
        workspace_id=workspace_id,
        **filter
    ).values_list("id", flat=True)

    filter = {"mapping__destination_id__in": destination_attribute_ids}

    expense_attributes_to_disable = ExpenseAttribute.objects.filter(
        attribute_type=source_field, active=True, **filter
    )

    expense_attributes_ids = []
    if expense_attributes_to_disable:
        expense_attributes_ids = [
            expense_attribute.id for expense_attribute in expense_attributes_to_disable
        ]
        expense_attributes_to_disable.update(active=False)

    return expense_attributes_ids


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


def remove_duplicates(xero_attributes: List[DestinationAttribute]):
    unique_attributes = []

    attribute_values = []

    for attribute in xero_attributes:
        if attribute.value.lower() not in attribute_values:
            unique_attributes.append(attribute)
            attribute_values.append(attribute.value.lower())

    return unique_attributes


def create_fyle_categories_payload(
    categories: List[DestinationAttribute],
    workspace_id: int,
    category_map: Dict,
    updated_categories: List[ExpenseAttribute] = None,
):
    """
    Create Fyle Categories Payload from Xero Categories
    :param workspace_id: Workspace integer id
    :param categories: Xero Categories
    :return: Fyle Categories Payload
    """
    payload = []

    if updated_categories:
        for category in updated_categories:
            destination_id_of_category = (
                category.mapping.first().destination.destination_id
            )
            payload.append(
                {
                    "id": category.source_id,
                    "name": category.value,
                    "code": destination_id_of_category,
                    "is_enabled": category.active if category.value != "Unspecified" else True
                }
            )
    else:
        for category in categories:
            if category.value.lower() not in category_map:
                payload.append(
                    {
                        "name": category.value,
                        "code": category.destination_id,
                        "is_enabled": category.active,
                    }
                )

    logger.info("| Importing Categories to Fyle | Content: {{Fyle Payload count: {}}}".format(len(payload)))
    return payload


def get_all_categories_from_fyle(platform: PlatformConnector):
    categories_generator = platform.connection.v1beta.admin.categories.list_all(
        query_params={"order": "id.desc"}
    )
    categories = []

    for response in categories_generator:
        if response.get("data"):
            categories.extend(response["data"])

    category_name_map = {}
    for category in categories:
        if category["sub_category"] and category["name"] != category["sub_category"]:
            category["name"] = "{0} / {1}".format(
                category["name"], category["sub_category"]
            )
        category_name_map[category["name"].lower()] = category

    return category_name_map


def upload_categories_to_fyle(workspace_id):
    """
    Upload categories to Fyle
    """
    fyle_credentials: FyleCredential = FyleCredential.objects.get(
        workspace_id=workspace_id
    )
    xero_credentials: XeroCredentials = XeroCredentials.get_active_xero_credentials(
        workspace_id
    )
    general_settings = WorkspaceGeneralSettings.objects.filter(
        workspace_id=workspace_id
    ).first()
    platform = PlatformConnector(fyle_credentials)

    category_map = get_all_categories_from_fyle(platform=platform)

    xero_connection = XeroConnector(
        credentials_object=xero_credentials, workspace_id=workspace_id
    )
    platform.categories.sync()
    xero_connection.sync_accounts()

    xero_attributes = DestinationAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type="ACCOUNT",
        detail__account_type__in=general_settings.charts_of_accounts,
    ).all()

    xero_attributes = remove_duplicates(xero_attributes)

    fyle_payload: List[Dict] = create_fyle_categories_payload(
        xero_attributes, workspace_id, category_map
    )

    if fyle_payload:
        platform.categories.post_bulk(fyle_payload)
        platform.categories.sync()

    category_ids_to_be_changed = disable_expense_attributes(
        FyleAttributeEnum.CATEGORY, "ACCOUNT", workspace_id
    )
    if category_ids_to_be_changed:
        expense_attributes = ExpenseAttribute.objects.filter(
            id__in=category_ids_to_be_changed
        )
        fyle_payload: List[Dict] = create_fyle_categories_payload(
            [], workspace_id, category_map, updated_categories=expense_attributes
        )
        platform.categories.post_bulk(fyle_payload)
        platform.categories.sync()

    logger.info("| Importing Categories to Fyle | Content: {{Fyle Payload count: {}}}".format(len(fyle_payload)))
    return xero_attributes


@handle_import_exceptions(task_name="auto create category mappings")
def auto_create_category_mappings(workspace_id):
    """
    Create Category Mappings
    :return: mappings
    """

    fyle_categories = upload_categories_to_fyle(workspace_id=workspace_id)

    Mapping.bulk_create_mappings(fyle_categories, FyleAttributeEnum.CATEGORY, "ACCOUNT", workspace_id)

    resolve_expense_attribute_errors(
        source_attribute_type=FyleAttributeEnum.CATEGORY, workspace_id=workspace_id
    )

    return []


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


def sync_xero_attributes(xero_attribute_type: str, workspace_id: int):
    xero_credentials: XeroCredentials = XeroCredentials.get_active_xero_credentials(
        workspace_id
    )
    xero_connection = XeroConnector(
        credentials_object=xero_credentials, workspace_id=workspace_id
    )

    if xero_attribute_type == "ITEM":
        xero_connection.sync_items()
    elif xero_attribute_type == "TAX_CODE":
        xero_connection.sync_tax_codes()
    elif xero_attribute_type == "CUSTOMER":
        xero_connection.sync_customers()
    else:
        xero_connection.sync_tracking_categories()


def upload_tax_groups_to_fyle(
    platform_connection: PlatformConnector, workspace_id: int
):
    existing_tax_codes_name = ExpenseAttribute.objects.filter(
        attribute_type=FyleAttributeEnum.TAX_GROUP, workspace_id=workspace_id
    ).values_list("value", flat=True)

    xero_attributes = DestinationAttribute.objects.filter(
        attribute_type="TAX_CODE", workspace_id=workspace_id
    ).order_by("value", "id")

    xero_attributes = remove_duplicates(xero_attributes)

    fyle_payload: List[Dict] = create_fyle_tax_group_payload(
        xero_attributes, existing_tax_codes_name
    )

    if fyle_payload:
        platform_connection.tax_groups.post_bulk(fyle_payload)

    platform_connection.tax_groups.sync()
    Mapping.bulk_create_mappings(xero_attributes, FyleAttributeEnum.TAX_GROUP, "TAX_CODE", workspace_id)


def create_fyle_tax_group_payload(
    xero_attributes: List[DestinationAttribute], existing_fyle_tax_groups: list
):
    """
    Create Fyle tax Group Payload from Xero Objects
    :param existing_fyle_tax_groups: Existing tax groups names
    :param xero_attributes: Xero Objects
    :return: Fyle tax Group Payload
    """

    existing_fyle_tax_groups = [
        tax_group.lower() for tax_group in existing_fyle_tax_groups
    ]

    fyle_tax_group_payload = []
    for xero_attribute in xero_attributes:
        if xero_attribute.value.lower() not in existing_fyle_tax_groups:
            fyle_tax_group_payload.append(
                {
                    "name": xero_attribute.value,
                    "is_enabled": True,
                    "percentage": round((xero_attribute.detail["tax_rate"] / 100), 2),
                }
            )

    logger.info("| Importing Tax Groups to Fyle | Content: {{Fyle Payload count: {}}}".format(len(fyle_tax_group_payload)))
    return fyle_tax_group_payload


@handle_import_exceptions(task_name="auto create tax codes_mappings")
def auto_create_tax_codes_mappings(workspace_id: int):
    """
    Create Tax Codes Mappings
    :return: None
    """

    fyle_credentials: FyleCredential = FyleCredential.objects.get(
        workspace_id=workspace_id
    )

    platform = PlatformConnector(fyle_credentials=fyle_credentials)
    platform.tax_groups.sync()

    sync_xero_attributes("TAX_CODE", workspace_id)

    upload_tax_groups_to_fyle(platform, workspace_id)


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

    if workspace_general_settings.import_categories:
        chain.append("apps.mappings.tasks.auto_create_category_mappings", workspace_id, q_options={
            'cluster': 'import'
        })

    if workspace_general_settings.import_suppliers_as_merchants:
        chain.append(
            "apps.mappings.tasks.auto_create_suppliers_as_merchants", workspace_id,
            q_options={
                'cluster': 'import'
            }
        )

    if chain.length() > 0:
        chain.run()
