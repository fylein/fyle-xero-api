import pytest
from django_q.models import Schedule
from fyle_accounting_mappings.models import DestinationAttribute, CategoryMapping, \
    Mapping, MappingSetting, EmployeeMapping
from apps.mappings.tasks import auto_create_tax_codes_mappings, schedule_tax_groups_creation,auto_create_project_mappings, \
    schedule_projects_creation, remove_duplicates, create_fyle_categories_payload, upload_categories_to_fyle, \
        schedule_categories_creation, auto_create_category_mappings, schedule_cost_centers_creation, \
            async_auto_map_employees, schedule_auto_map_employees, get_all_categories_from_fyle, \
                auto_create_cost_center_mappings, schedule_fyle_attributes_creation, \
                    async_auto_create_custom_field_mappings, auto_create_expense_fields_mappings
from fyle_integrations_platform_connector import PlatformConnector
from ..test_xero.fixtures import data as xero_data
from .fixtures import data
from tests.helper import dict_compare_keys
from apps.workspaces.models import XeroCredentials, FyleCredential, WorkspaceGeneralSettings 


def test_auto_create_tax_codes_mappings(db, mocker):
    workspace_id = 1
    mocker.patch(
        'fyle_integrations_platform_connector.apis.TaxGroups.post_bulk',
        return_value=[]
    )

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()
    
    assert tax_groups == 8
    assert mappings == 8

    auto_create_tax_codes_mappings(workspace_id=workspace_id)

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()
    
    assert mappings == 8

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_tax_codes_mappings(workspace_id)

    assert response == None

def test_schedule_tax_groups_creation(db):
    workspace_id = 1
    schedule_tax_groups_creation(import_tax_codes=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_tax_codes_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_tax_codes_mappings'

    schedule_tax_groups_creation(import_tax_codes=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_tax_codes_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_auto_create_project_mappings(db, mocker):
    workspace_id = 1
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Projects.post_bulk',
        return_value=[]
    )
    
    response = auto_create_project_mappings(workspace_id=workspace_id)
    assert response == None

    projects = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='PROJECT').count()

    assert mappings == projects

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_project_mappings(workspace_id=workspace_id)

    assert response == None


@pytest.mark.django_db
def test_schedule_projects_creation(db):
    workspace_id = 1
    schedule_projects_creation(import_to_fyle=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_project_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_project_mappings'

    schedule_projects_creation(import_to_fyle=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_project_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_remove_duplicates(db):

    attributes = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE')
    assert len(attributes) == 0

    attributes = remove_duplicates(attributes)
    assert len(attributes) == 0


def test_upload_categories_to_fyle(db):
    workspace_id = 1

    xero_attributes = upload_categories_to_fyle(workspace_id=workspace_id)
    assert xero_attributes == []

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_credentials.delete()

    xero_attributes = upload_categories_to_fyle(workspace_id=workspace_id)
    assert xero_attributes == None


def test_create_fyle_category_payload(db):
    workspace_id = 1
    qbo_attributes = DestinationAttribute.objects.filter(
        workspace_id=1, attribute_type='ACCOUNT'
    )

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    category_map = get_all_categories_from_fyle(platform=platform)
    fyle_category_payload = create_fyle_categories_payload(qbo_attributes, 2, category_map)
    
    assert dict_compare_keys(fyle_category_payload[0], data['fyle_category_payload'][0]) == [], 'category upload api return diffs in keys'


def test_upload_categories_to_fyle(mocker, db):
    workspace_id = 1
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Categories.post_bulk',
        return_value='nilesh'
    )

    count_of_accounts = DestinationAttribute.objects.filter(
        attribute_type='ACCOUNT', workspace_id=workspace_id).count()
    
    assert count_of_accounts == 56


def test_auto_create_category_mappings(db, mocker): #needs refresh token
    workspace_id = 1
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Categories.post_bulk',
        return_value=[]
    )

    mocker.patch(
        'xerosdk.apis.Accounts.get_all',
        return_value=xero_data['get_all_accounts']
    )

    response = auto_create_category_mappings(workspace_id=workspace_id)
    assert response == []

    mappings = CategoryMapping.objects.filter(workspace_id=workspace_id)

    assert len(mappings) == 0

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_category_mappings(workspace_id=workspace_id)

    assert response == None


def test_schedule_categories_creation(db):
    workspace_id = 1
    schedule_categories_creation(import_categories=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_category_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_category_mappings'

    schedule_categories_creation(import_categories=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_category_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_async_auto_map_employees(db):  #needs refresh token
    workspace_id = 1

    async_auto_map_employees(workspace_id)
    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 0

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.employee_field_mapping = 'VENDOR'
    general_settings.save()

    async_auto_map_employees(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 0

    qbo_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    qbo_credentials.delete()

    async_auto_map_employees(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 0


def test_schedule_auto_map_employees(db):
    workspace_id = 1

    schedule_auto_map_employees(employee_mapping_preference=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_map_employees',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.async_auto_map_employees'

    schedule_auto_map_employees(employee_mapping_preference=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_map_employees',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_auto_create_cost_center_mappings(db, mocker, create_mapping_setting):
    workspace_id = 1
    mocker.patch(
            'fyle_integrations_platform_connector.apis.CostCenters.post_bulk',
            return_value=[]
        )
    
    response = auto_create_cost_center_mappings(workspace_id=workspace_id)
    assert response == None

    cost_center = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER').count()

    assert cost_center == 1
    assert mappings == 0

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_cost_center_mappings(workspace_id=workspace_id)
    assert response == None


def test_schedule_cost_centers_creation(db):
    workspace_id = 1

    schedule_cost_centers_creation(import_to_fyle=True, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_cost_center_mappings',
        args='{}'.format(workspace_id),
    ).first()
    
    assert schedule.func == 'apps.mappings.tasks.auto_create_cost_center_mappings'

    schedule_cost_centers_creation(import_to_fyle=False, workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_create_cost_center_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None


def test_schedule_fyle_attributes_creation(db, mocker):
    workspace_id = 1

    mapping_setting = MappingSetting.objects.last()
    mapping_setting.is_custom=True
    mapping_setting.import_to_fyle=True
    mapping_setting.save()
    
    schedule_fyle_attributes_creation(workspace_id)

    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.post',
        return_value=[]
    )

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_create_custom_field_mappings'

    async_auto_create_custom_field_mappings(workspace_id)

    schedule_fyle_attributes_creation(2)
    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_create_custom_field_mappings'


def test_auto_create_expense_fields_mappings(db, mocker, create_mapping_setting):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.post',
        return_value=[]
    )
    workspace_id = 1

    auto_create_expense_fields_mappings(workspace_id, 'COST_CENTER', 'COST_CENTER')

    cost_center = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER').count()

    assert cost_center == 1
    assert mappings == 0
    