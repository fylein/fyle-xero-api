from unittest import mock

import pytest
from django.core.cache import cache
from fyle_accounting_mappings.models import ExpenseAttribute

from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.modules.webhook_attributes import WebhookAttributeProcessor
from tests.test_fyle.fixtures import data


@pytest.mark.django_db
def test_process_webhook_category_created(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['category_created']
    initial_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'Travel / Flight'
    assert expense_attr.active is True
    final_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CATEGORY').count()
    assert final_count > initial_count


@pytest.mark.django_db
def test_process_webhook_category_updated(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_456'
    ).delete()
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_456',
        value='Old Travel',
        active=True
    )
    webhook_body = data['webhook_attribute_payloads']['category_updated']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_456'
    ).order_by('-updated_at').first()

    assert expense_attr is not None
    assert expense_attr.value == 'New Travel / Train'
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_webhook_category_deleted(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        source_id='cat_789',
        value='Old Category',
        active=True
    )
    webhook_body = data['webhook_attribute_payloads']['category_deleted']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        source_id='cat_789'
    )

    assert expense_attr.active is False


@pytest.mark.django_db
def test_process_webhook_project(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['project_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='PROJECT',
        source_id='proj_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'Main Project / Sub Project 1'
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_webhook_employee(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['employee_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='EMPLOYEE',
        source_id='emp_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'employee@example.com'
    assert expense_attr.detail['user_id'] == 'user_123'
    assert expense_attr.detail['employee_code'] == 'EMP001'
    assert expense_attr.detail['full_name'] == 'John Doe'
    assert expense_attr.detail['location'] == 'New York'
    assert expense_attr.detail['department'] == 'Engineering'
    assert expense_attr.detail['department_code'] == 'ENG'


@pytest.mark.django_db
def test_process_webhook_corporate_card(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['corporate_card_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CORPORATE_CARD',
        source_id='card_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'Chase - 23456'
    assert expense_attr.detail['cardholder_name'] == 'Jane Smith'
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_webhook_tax_group(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['tax_group_created']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='TAX_GROUP',
        source_id='tax_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'GST 18%'
    assert expense_attr.detail['tax_rate'] == 18.0
    assert expense_attr.active is True


@pytest.mark.django_db
def test_process_expense_field_select_type(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['expense_field_select_created']
    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='DEPARTMENT'
    ).count()
    processor.process_webhook(webhook_body)

    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='DEPARTMENT'
    ).count()

    assert final_count == initial_count + 3
    sales = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='DEPARTMENT',
        value='Sales'
    ).first()
    assert sales is not None
    assert sales.detail['custom_field_id'] == 'field_123'
    assert sales.detail['is_mandatory'] is True


@pytest.mark.django_db
def test_process_expense_field_disable_options(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='North',
        source_id='field_456',
        active=True
    )
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='South',
        source_id='field_456',
        active=True
    )
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='East',
        source_id='field_456',
        active=True
    )
    webhook_body = data['webhook_attribute_payloads']['expense_field_region_updated']
    processor.process_webhook(webhook_body)
    east = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='East'
    )
    assert east.active is False
    north = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        attribute_type='REGION',
        value='North'
    )
    assert north.active is True


@pytest.mark.django_db
def test_process_expense_field_non_select_type(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['expense_field_text_created']
    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='NOTES'
    ).count()
    processor.process_webhook(webhook_body)
    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='NOTES'
    ).count()
    assert final_count == initial_count


@pytest.mark.django_db
def test_process_webhook_skip_when_import_in_progress(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    cache.clear()
    ImportLog.objects.create(
        workspace_id=workspace_id,
        attribute_type='CATEGORY',
        status='IN_PROGRESS'
    )
    webhook_body = data['webhook_attribute_payloads']['category_skip']
    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY'
    ).count()
    processor.process_webhook(webhook_body)
    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace_id,
        attribute_type='CATEGORY'
    ).count()
    assert final_count == initial_count
    cache.clear()


@pytest.mark.django_db
def test_process_webhook_deleted_ignores_import_in_progress(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    cache.clear()
    ExpenseAttribute.objects.create(
        workspace_id=workspace_id,
        attribute_type='COST_CENTER',
        source_id='cc_delete',
        value='To Be Deleted',
        active=True
    )
    ImportLog.objects.create(
        workspace_id=workspace_id,
        attribute_type='COST_CENTER',
        status='IN_PROGRESS'
    )
    webhook_body = data['webhook_attribute_payloads']['cost_center_deleted']
    processor.process_webhook(webhook_body)
    expense_attr = ExpenseAttribute.objects.get(
        workspace_id=workspace_id,
        source_id='cc_delete'
    )
    assert expense_attr.active is False
    cache.clear()


@pytest.mark.django_db
def test_process_webhook_unsupported_resource_type(db):
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)
    webhook_body = data['webhook_attribute_payloads']['unsupported_resource']
    initial_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id).count()
    processor.process_webhook(webhook_body)
    final_count = ExpenseAttribute.objects.filter(workspace_id=workspace_id).count()
    assert final_count == initial_count


@pytest.mark.django_db
def test_process_webhook_corporate_card_created_triggers_patch(db, mocker):
    """Test CORPORATE_CARD CREATED webhook triggers patch and handles exceptions"""
    workspace_id = 1
    processor = WebhookAttributeProcessor(workspace_id)

    with mock.patch('apps.mappings.helpers.patch_corporate_card_integration_settings') as mock_patch:
        processor.process_webhook(data['webhook_attribute_payloads']['corporate_card_created'])
        mock_patch.assert_called_once_with(workspace_id=workspace_id)

    with mock.patch('apps.mappings.helpers.patch_corporate_card_integration_settings') as mock_patch:
        mock_patch.side_effect = Exception("Test error")
        processor.process_webhook(data['webhook_attribute_payloads']['corporate_card_created'])
        assert ExpenseAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CORPORATE_CARD',
                                              source_id='card_123').exists()
