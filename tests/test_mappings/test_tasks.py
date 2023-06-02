import pytest
from unittest import mock
from django_q.models import Schedule
from fyle_accounting_mappings.models import DestinationAttribute, CategoryMapping, \
    Mapping, MappingSetting, EmployeeMapping
from apps.mappings.tasks import *
from fyle_integrations_platform_connector import PlatformConnector
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError, InternalServerError
from ..test_xero.fixtures import data as xero_data
from ..test_fyle.fixtures import data as fyle_data
from .fixtures import data
from tests.helper import dict_compare_keys
from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.workspaces.models import XeroCredentials, FyleCredential, WorkspaceGeneralSettings 


def test_auto_create_tax_codes_mappings(db, mocker):
    workspace_id = 1
    mocker.patch(
        'fyle_integrations_platform_connector.apis.TaxGroups.post_bulk',
        return_value=[]
    )

    mocker.patch(
        'fyle_integrations_platform_connector.apis.TaxGroups.sync',
        return_value=[]
    )

    mocker.patch(
        'xerosdk.apis.TaxRates.get_all',
        return_value=xero_data['get_all_tax_codes']
    )

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()
    
    assert tax_groups == 8
    assert mappings == 8

    existing_tax_codes_name = ExpenseAttribute.objects.filter(
        attribute_type='TAX_GROUP', workspace_id=workspace_id).first()
    existing_tax_codes_name.value = 'wertyuio'
    existing_tax_codes_name.save()

    auto_create_tax_codes_mappings(workspace_id=workspace_id)

    tax_groups = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='TAX_CODE').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='TAX_CODE').count()
    
    assert mappings == 8

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_tax_codes_mappings(workspace_id)
    assert response == None

    with mock.patch('fyle_integrations_platform_connector.apis.TaxGroups.sync') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong parameter error', response="wrong parameter error")
        response = auto_create_tax_codes_mappings(workspace_id=workspace_id)

        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for Fyle', response="Invalid Token for Fyle")
        response = auto_create_tax_codes_mappings(workspace_id=workspace_id)

        mock_call.side_effect = InternalServerError(msg='Internal server error while importing to Fyle', response="Internal server error while importing to Fyle")
        response = auto_create_tax_codes_mappings(workspace_id=workspace_id)

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
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Projects.sync',
        return_value=[]
    )
    mocker.patch(
        'xerosdk.apis.Contacts.list_all_generator',
        return_value=xero_data['get_all_contacts']
    )
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_customers',
        return_value=[]
    )
    existing_project_names = ExpenseAttribute.objects.filter(
        attribute_type='PROJECT', workspace_id=workspace_id).first()
    existing_project_names.value = 'asdfghj'
    existing_project_names.save()

    response = auto_create_project_mappings(workspace_id=workspace_id)
    assert response == None

    projects = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='PROJECT').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, destination_type='PROJECT').count()
    assert mappings == projects

    with mock.patch('apps.xero.utils.XeroConnector.sync_customers') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong parameter error', response="wrong parameter error")
        response = auto_create_project_mappings(workspace_id=workspace_id)

        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for Fyle', response="Invalid Token for Fyle")
        response = auto_create_project_mappings(workspace_id=workspace_id)

        mock_call.side_effect = InternalServerError(msg='Internal server error while importing to Fyle', response="Internal server error while importing to Fyle")
        response = auto_create_project_mappings(workspace_id=workspace_id)

        mock_call.side_effect = Exception()
        response = auto_create_project_mappings(workspace_id=workspace_id)

def test_remove_duplicates(db):

    attributes = DestinationAttribute.objects.filter(attribute_type='EMPLOYEE')
    assert len(attributes) == 0

    attributes = remove_duplicates(attributes)
    assert len(attributes) == 0


def test_upload_categories_to_fyle(db, mocker):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Categories.post_bulk',
        return_value=[]
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Categories.sync',
        return_value=[]
    )
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Categories.list_all',
        return_value=fyle_data['get_all_categories']
    )
    mocker.patch(
        'apps.xero.utils.XeroConnector.sync_accounts',
        return_value=[]
    )

    workspace_id = 1

    da_instance = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type="ACCOUNT").first()
    da_instance.active = False
    da_instance.save()

    ea_instance = ExpenseAttribute.objects.filter(attribute_type="CATEGORY").first()
    ea_instance.active = True

    mapping_instance = Mapping.objects.create(destination_type="ACCOUNT",destination=da_instance,workspace_id=workspace_id,source=ea_instance)

    ea_instance.save()

    xero_attributes = upload_categories_to_fyle(workspace_id=workspace_id)
    assert len(xero_attributes) == 29

    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_credentials.delete()

    # Expect XeroCredentials.DoesNotExist exception since we've deleted the credentials
    with pytest.raises(XeroCredentials.DoesNotExist):
        xero_attributes = upload_categories_to_fyle(workspace_id=workspace_id)

def test_create_fyle_category_payload(mocker, db):
    workspace_id = 1
    qbo_attributes = DestinationAttribute.objects.filter(
        workspace_id=1, attribute_type='ACCOUNT'
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Categories.list_all',
        return_value=fyle_data['get_all_categories']
    )

    qbo_attributes = remove_duplicates(qbo_attributes)

    fyle_credentials: FyleCredential = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentials)

    category_map = get_all_categories_from_fyle(platform=platform)
    fyle_category_payload = create_fyle_categories_payload(qbo_attributes, 2, category_map)
    
    assert dict_compare_keys(fyle_category_payload[0], data['fyle_category_payload'][0]) == [], 'category upload api return diffs in keys'


def test_auto_create_category_mappings(db, mocker):
    workspace_id = 1
    mocker.patch(
        'fyle_integrations_platform_connector.apis.Categories.post_bulk',
        return_value=[]
    )

    mocker.patch(
        'xerosdk.apis.Accounts.get_all',
        return_value=xero_data['get_all_accounts']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Categories.list_all',
        return_value=fyle_data['get_all_categories']
    )

    response = auto_create_category_mappings(workspace_id=workspace_id)
    assert response == []

    mappings = CategoryMapping.objects.filter(workspace_id=workspace_id)

    assert len(mappings) == 0

    with mock.patch('apps.mappings.tasks.upload_categories_to_fyle') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong parameter error', response="wrong parameter error")
        response = auto_create_category_mappings(workspace_id=workspace_id)

        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for Fyle', response="Invalid Token for Fyle")
        response = auto_create_category_mappings(workspace_id=workspace_id)

        mock_call.side_effect = InternalServerError(msg='Internal server error while importing to Fyle', response="Internal server error while importing to Fyle")
        response = auto_create_category_mappings(workspace_id=workspace_id)

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    fyle_credentials.delete()

    response = auto_create_category_mappings(workspace_id=workspace_id)

    assert response == None

def test_async_auto_map_employees(mocker, db):
    workspace_id = 1

    mocker.patch(
        'xerosdk.apis.Contacts.list_all_generator',
        return_value=xero_data['get_all_contacts']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Employees.list_all',
        return_value=fyle_data['get_all_employees']
    )

    async_auto_map_employees(workspace_id)
    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 0

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    general_settings.employee_field_mapping = 'VENDOR'
    general_settings.save()

    async_auto_map_employees(workspace_id)

    employee_mappings = EmployeeMapping.objects.filter(workspace_id=workspace_id).count()
    assert employee_mappings == 0

    with mock.patch('fyle.platform.apis.v1beta.admin.Employees.list_all') as mock_call:
        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for Fyle', response="Invalid Token for Fyle")
        async_auto_map_employees(workspace_id=workspace_id)

        mock_call.side_effect = UnsuccessfulAuthentication(msg='Auth error')
        async_auto_map_employees(workspace_id=workspace_id)

        mock_call.side_effect = InternalServerError(msg='Internal server error while importing to Fyle')
        async_auto_map_employees(workspace_id=workspace_id)

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
    
    mocker.patch(
        'fyle_integrations_platform_connector.apis.CostCenters.sync',
        return_value=[]
    )
    
    mocker.patch(
        'xerosdk.apis.TrackingCategories.get_all',
        return_value=xero_data['get_all_tracking_categories']
    )
    
    response = auto_create_cost_center_mappings(workspace_id=workspace_id)
    assert response == None

    cost_center = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER').count()

    assert cost_center == 1
    assert mappings == 0

    with mock.patch('fyle_integrations_platform_connector.apis.CostCenters.sync') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong parameter error', response="wrong parameter error")
        response = auto_create_cost_center_mappings(workspace_id=workspace_id)

        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for Fyle', response="Inalid Token for Fyle")
        response = auto_create_cost_center_mappings(workspace_id=workspace_id)

        mock_call.side_effect = InternalServerError(msg='Internal server error while importing to Fyle', response="Internal server error while importing to Fyle")
        response = auto_create_cost_center_mappings(workspace_id=workspace_id)

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

    mocker.patch(
        'xerosdk.apis.TrackingCategories.get_all',
        return_value=xero_data['get_all_tracking_categories']
    )

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule.func == 'apps.mappings.tasks.async_auto_create_custom_field_mappings'

    async_auto_create_custom_field_mappings(workspace_id)

    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()
    mapping_settings.delete()

    schedule_fyle_attributes_creation(workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.async_auto_create_custom_field_mappings',
        args='{}'.format(workspace_id),
    ).count()

    assert schedule == 0


def test_auto_create_expense_fields_mappings(db, mocker, create_mapping_setting):
    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.post',
        return_value=[]
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.sync',
        return_value=[]
    )
    mocker.patch(
        'fyle_integrations_platform_connector.apis.ExpenseCustomFields.get_by_id',
        return_value={'options': ['samp'], 'updated_at': '2020-06-11T13:14:55.201598+00:00', 'is_mandatory': True}
    )
    workspace_id = 1

    auto_create_expense_fields_mappings(workspace_id, 'COST_CENTER', 'TESTING_THIS')

    cost_center = DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='COST_CENTER').count()
    mappings = Mapping.objects.filter(workspace_id=workspace_id, source_type='COST_CENTER').count()

    assert cost_center == 1
    assert mappings == 0

    with mock.patch('fyle_integrations_platform_connector.apis.ExpenseCustomFields.post') as mock_call:
        mock_call.side_effect = WrongParamsError(msg='wrong parameter error', response="wrong parameter error")
        auto_create_expense_fields_mappings(workspace_id, 'COST_CENTER', 'TESTING_THIS')

        mock_call.side_effect = FyleInvalidTokenError(msg='Invalid Token for Fyle', response="Invalid Token for Fyle")
        auto_create_expense_fields_mappings(workspace_id, 'COST_CENTER', 'TESTING_THIS')

        mock_call.side_effect = InternalServerError(msg='Internal server error while importing to Fyle', response="Internal server error while importing to Fyle")
        auto_create_expense_fields_mappings(workspace_id, 'COST_CENTER', 'TESTING_THIS')

        mock_call.side_effect = Exception()
        auto_create_expense_fields_mappings(workspace_id, 'COST_CENTER', 'TESTING_THIS')


def test_resolve_expense_attribute_errors(db):
    workspace_id = 1
    expense_group = ExpenseGroup.objects.get(id=3)

    employee_attribute = ExpenseAttribute.objects.filter(
        value=expense_group.description.get('employee_email'),
        workspace_id=expense_group.workspace_id,
        attribute_type='EMPLOYEE'
    ).first()

    mapping = Mapping.objects.get(
        destination_type='CONTACT',
        source_type='EMPLOYEE',
        source=employee_attribute,
        workspace_id=expense_group.workspace_id
    )

    error, _ = Error.objects.update_or_create(
        workspace_id=expense_group.workspace_id,
        expense_attribute=employee_attribute,
        defaults={
            'type': 'EMPLOYEE_MAPPING',
            'error_title': employee_attribute.value,
            'error_detail': 'Employee mapping is missing',
            'is_resolved': False
        }
    )

    resolve_expense_attribute_errors('EMPLOYEE', workspace_id, 'CONTACT')
    assert Error.objects.get(id=error.id).is_resolved == True

def test_auto_import_and_map_fyle_fields(db):
    workspace_id = 1

    auto_import_and_map_fyle_fields(workspace_id=workspace_id)

    schedule = Schedule.objects.filter(
        func='apps.mappings.tasks.auto_import_and_map_fyle_fields',
        args='{}'.format(workspace_id),
    ).first()

    assert schedule == None
