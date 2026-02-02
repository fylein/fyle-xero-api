import pytest

from apps.workspaces.models import WorkspaceGeneralSettings
from apps.xero.actions import refresh_xero_dimension


@pytest.mark.django_db
def test_refresh_xero_dimension_with_general_settings(mocker):
    """
    Test refresh_xero_dimension when WorkspaceGeneralSettings exist
    This covers lines 41 and 48 in apps/xero/actions.py
    """
    workspace_id = 1

    # Ensure WorkspaceGeneralSettings exists
    WorkspaceGeneralSettings.objects.get_or_create(
        workspace_id=workspace_id,
        defaults={'reimbursable_expenses_object': 'BILL'}
    )

    # Mock the xero connector and publish
    mock_xero_connector = mocker.patch('apps.xero.actions.get_xero_connector')
    mock_publish = mocker.patch('apps.xero.actions.publish_to_rabbitmq')

    refresh_xero_dimension(workspace_id)

    # Verify publish_to_rabbitmq was called for IMPORT_DIMENSIONS_TO_FYLE
    mock_publish.assert_called_once()
    call_args = mock_publish.call_args
    payload = call_args[1]['payload']
    assert payload['action'] == 'IMPORT.IMPORT_DIMENSIONS_TO_FYLE'
    assert payload['workspace_id'] == workspace_id

    # Verify sync_dimensions was called
    mock_xero_connector.return_value.sync_dimensions.assert_called_once_with(workspace_id)


@pytest.mark.django_db
def test_refresh_xero_dimension_without_general_settings(mocker):
    """
    Test refresh_xero_dimension when WorkspaceGeneralSettings do NOT exist
    """
    workspace_id = 1

    # Delete WorkspaceGeneralSettings if exists
    WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).delete()

    # Mock the xero connector and publish
    mock_xero_connector = mocker.patch('apps.xero.actions.get_xero_connector')
    mock_publish = mocker.patch('apps.xero.actions.publish_to_rabbitmq')

    refresh_xero_dimension(workspace_id)

    # Verify publish_to_rabbitmq was NOT called
    mock_publish.assert_not_called()

    # Verify sync_dimensions was still called
    mock_xero_connector.return_value.sync_dimensions.assert_called_once_with(workspace_id)
