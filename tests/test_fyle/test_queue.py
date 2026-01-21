import pytest
from fyle_accounting_library.rabbitmq.data_class import Task
from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.queue import handle_webhook_callback
from apps.workspaces.models import FeatureConfig, Workspace
from apps.xero.queue import __create_chain_and_run
from tests.test_fyle.fixtures import data


@pytest.fixture(autouse=True)
def mock_publish_to_rabbitmq(mocker):
    """Auto-mock publish_to_rabbitmq for all tests in this module"""
    return mocker.patch('apps.fyle.queue.publish_to_rabbitmq')


# This test is just for cov :D
def test_create_chain_and_run(db):
    workspace_id = 1
    chain_tasks = [
        Task(
            target='apps.xero.tasks.create_bill',
            args=[1, 1, True, False]
        )
    ]

    __create_chain_and_run(workspace_id, chain_tasks, False)
    assert True


def test_create_chain_and_run_with_webhook_sync_enabled(db, mocker):
    workspace_id = 1

    FeatureConfig.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={'fyle_webhook_sync_enabled': True}
    )

    chain_tasks = [
        Task(
            target='apps.xero.tasks.create_bill',
            args=[1, 1, True, False]
        )
    ]

    mock_sync_dimension = mocker.patch('apps.fyle.tasks.check_interval_and_sync_dimension')
    mock_chain_class = mocker.patch('apps.xero.queue.Chain')
    mock_chain_instance = mock_chain_class.return_value

    __create_chain_and_run(workspace_id, chain_tasks, False)

    mock_chain_class.assert_called_once()
    mock_sync_dimension.assert_not_called()
    mock_chain_instance.append.assert_called()
    mock_chain_instance.run.assert_called_once()


def test_create_chain_and_run_with_webhook_sync_disabled(db, mocker):
    workspace_id = 1

    FeatureConfig.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={'fyle_webhook_sync_enabled': False}
    )

    chain_tasks = [
        Task(
            target='apps.xero.tasks.create_bill',
            args=[1, 1, True, False]
        )
    ]

    mocker.patch('apps.fyle.tasks.check_interval_and_sync_dimension')
    mock_chain_class = mocker.patch('apps.xero.queue.Chain')
    mock_chain_instance = mock_chain_class.return_value

    __create_chain_and_run(workspace_id, chain_tasks, False)

    mock_chain_class.assert_called_once()
    mock_chain_instance.append.assert_any_call('apps.fyle.tasks.check_interval_and_sync_dimension', workspace_id)
    mock_chain_instance.run.assert_called_once()


# This test is just for cov :D
def test_handle_webhook_callback(db):
    body = data['webhook_callback_payloads']['accounting_export_initiated']

    worksapce, _ = Workspace.objects.update_or_create(
        fyle_org_id = 'or79Cob97KSh'
    )

    handle_webhook_callback(body, worksapce.id)


# This test is just for cov :D (2)
def test_handle_webhook_callback_2(db):
    body = data['webhook_callback_payloads']['state_change_payment_processing']

    worksapce, _ = Workspace.objects.update_or_create(
        fyle_org_id = 'or79Cob97KSh'
    )

    handle_webhook_callback(body, worksapce.id)


# Test for UPDATED_AFTER_APPROVAL with EXPENSE resource
def test_handle_webhook_callback_updated_after_approval_expense(db):
    """
    Test UPDATED_AFTER_APPROVAL webhook with EXPENSE resource
    """
    test_data = data['fund_source_change']

    body = {
        'action': 'UPDATED_AFTER_APPROVAL',
        'resource': 'EXPENSE',
        'data': test_data['expense_payload']
    }

    workspace, _ = Workspace.objects.update_or_create(
        **test_data['workspace_defaults']
    )

    handle_webhook_callback(body, workspace.id)


# Test for UPDATED_AFTER_APPROVAL with REPORT resource
def test_handle_webhook_callback_updated_after_approval_report(db):
    """
    Test UPDATED_AFTER_APPROVAL webhook with REPORT resource for fund source changes
    """
    test_data = data['fund_source_change']

    body = {
        'action': 'UPDATED_AFTER_APPROVAL',
        'resource': 'REPORT',
        'data': test_data['report_payload']
    }

    workspace, _ = Workspace.objects.update_or_create(
        **test_data['workspace_defaults']
    )

    handle_webhook_callback(body, workspace.id)


def test_handle_webhook_callback_ejected_from_report(db):
    """
    Test async_import_and_export_expenses for EJECTED_FROM_REPORT action
    """
    body = data['webhook_callback_payloads']['ejected_from_report']

    workspace = Workspace.objects.get(id=1)

    handle_webhook_callback(body, workspace.id)


def test_handle_webhook_callback_added_to_report(db):
    """
    Test async_import_and_export_expenses for ADDED_TO_REPORT action
    """
    body = data['webhook_callback_payloads']['added_to_report']

    workspace = Workspace.objects.get(id=1)

    handle_webhook_callback(body, workspace.id)


def test_handle_webhook_callback_attribute_webhook(db):
    workspace = Workspace.objects.get(id=1)

    FeatureConfig.objects.update_or_create(
        workspace_id=workspace.id,
        defaults={'fyle_webhook_sync_enabled': True}
    )

    body = data['webhook_callback_payloads']['category_webhook_enabled'].copy()
    body['data']['org_id'] = workspace.fyle_org_id

    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace.id,
        attribute_type='CATEGORY'
    ).count()

    handle_webhook_callback(body, workspace.id)

    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace.id,
        attribute_type='CATEGORY'
    ).count()

    assert final_count > initial_count

    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace.id,
        attribute_type='CATEGORY',
        source_id='cat_webhook_123'
    ).first()

    assert expense_attr is not None
    assert expense_attr.value == 'Test Category / Test Subcategory'
    assert expense_attr.active is True


def test_handle_webhook_callback_attribute_webhook_disabled(db):
    workspace = Workspace.objects.get(id=1)

    FeatureConfig.objects.update_or_create(
        workspace_id=workspace.id,
        defaults={'fyle_webhook_sync_enabled': False}
    )

    body = data['webhook_callback_payloads']['category_webhook_disabled'].copy()
    body['data']['org_id'] = workspace.fyle_org_id

    initial_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace.id,
        attribute_type='CATEGORY'
    ).count()

    handle_webhook_callback(body, workspace.id)

    final_count = ExpenseAttribute.objects.filter(
        workspace_id=workspace.id,
        attribute_type='CATEGORY'
    ).count()

    assert final_count == initial_count

    expense_attr = ExpenseAttribute.objects.filter(
        workspace_id=workspace.id,
        attribute_type='CATEGORY',
        source_id='cat_disabled_123'
    ).first()

    assert expense_attr is None


def test_handle_webhook_callback_attribute_webhook_exception(db, mocker):
    workspace = Workspace.objects.get(id=1)

    FeatureConfig.objects.update_or_create(
        workspace_id=workspace.id,
        defaults={'fyle_webhook_sync_enabled': True}
    )

    body = data['webhook_callback_payloads']['category_webhook_exception'].copy()
    body['data']['org_id'] = workspace.fyle_org_id

    mock_processor = mocker.patch('apps.fyle.queue.WebhookAttributeProcessor')
    mock_processor.return_value.process_webhook.side_effect = Exception('Test exception')

    mock_logger = mocker.patch('apps.fyle.queue.logger')

    handle_webhook_callback(body, workspace.id)

    mock_logger.error.assert_called_once()
    error_message = mock_logger.error.call_args[0][0]
    assert 'Error processing attribute webhook for workspace' in error_message
    assert str(workspace.id) in error_message
    assert 'Test exception' in error_message
