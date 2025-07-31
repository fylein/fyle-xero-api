import json
from unittest.mock import MagicMock

import pytest

from apps.workspaces.actions import patch_integration_settings
from apps.workspaces.helpers import patch_integration_settings_for_unmapped_cards
from apps.workspaces.models import LastExportDetail, Workspace


@pytest.mark.django_db(databases=['default'])
def test_patch_integration_settings(mocker):

    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    workspace.onboarding_state = 'COMPLETE'
    workspace.save()

    # Create a mock response object with the expected attributes
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"success": true}'

    # Mock requests.patch to return the mock response
    mocked_patch = mocker.patch('apps.fyle.helpers.requests.patch', return_value=mock_response)

    # Test patch request with only errors
    errors = 7
    patch_integration_settings(workspace_id, errors)

    expected_payload = {'errors_count': errors, 'tpa_name': 'Fyle Xero Integration'}

    # Get the call arguments from the mock
    _, kwargs = mocked_patch.call_args
    actual_payload = json.loads(kwargs['data'])

    assert actual_payload == expected_payload

    # Test patch request with only is_token_expired
    is_token_expired = True
    patch_integration_settings(workspace_id, is_token_expired=is_token_expired)

    expected_payload = {'is_token_expired': is_token_expired, 'tpa_name': 'Fyle Xero Integration'}

    _, kwargs = mocked_patch.call_args
    actual_payload = json.loads(kwargs['data'])

    assert actual_payload == expected_payload

    # Test patch request with errors_count and is_token_expired
    is_token_expired = True
    errors = 241
    patch_integration_settings(workspace_id, errors=errors, is_token_expired=is_token_expired)

    expected_payload = {
        'errors_count': errors,
        'is_token_expired': is_token_expired,
        'tpa_name': 'Fyle Xero Integration'
    }

    _, kwargs = mocked_patch.call_args
    actual_payload = json.loads(kwargs['data'])

    assert actual_payload == expected_payload

    # Test patch request with only unmapped_card_count
    unmapped_card_count = 1
    is_patched = patch_integration_settings(workspace_id, unmapped_card_count=unmapped_card_count)

    expected_payload = {'unmapped_card_count': unmapped_card_count, 'tpa_name': 'Fyle Xero Integration'}

    _, kwargs = mocked_patch.call_args
    actual_payload = json.loads(kwargs['data'])

    assert actual_payload == expected_payload
    assert is_patched == True

    # Test exception handling - should return False when an exception occurs
    mocked_patch.side_effect = Exception("Network error")
    is_patched = patch_integration_settings(workspace_id, errors=5)
    assert is_patched == False


@pytest.mark.django_db(databases=['default'])
def test_patch_integration_settings_for_unmapped_cards(mocker):

    workspace_id = 1
    workspace = Workspace.objects.get(id=workspace_id)
    workspace.onboarding_state = 'COMPLETE'
    workspace.save()
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)

    # Mock the patch_integration_settings function
    mocked_patch_integration_settings = MagicMock(return_value=True)
    mocker.patch('apps.workspaces.helpers.patch_integration_settings', side_effect=mocked_patch_integration_settings)

    # Test patch request when unmapped_card_count is different and patch is successful
    new_unmapped_card_count = 10
    patch_integration_settings_for_unmapped_cards(workspace_id, new_unmapped_card_count)

    # Verify patch_integration_settings was called with correct parameters
    mocked_patch_integration_settings.assert_called_once_with(
        workspace_id=workspace_id,
        unmapped_card_count=new_unmapped_card_count
    )

    # Verify LastExportDetail was updated
    last_export_detail.refresh_from_db()
    assert last_export_detail.unmapped_card_count == new_unmapped_card_count

    # Reset mock for next test
    mocked_patch_integration_settings.reset_mock()

    # Test patch request when unmapped_card_count is the same - should not call patch
    patch_integration_settings_for_unmapped_cards(workspace_id, new_unmapped_card_count)

    # Verify patch_integration_settings was not called
    mocked_patch_integration_settings.assert_not_called()

    # Reset mock for next test
    mocked_patch_integration_settings.reset_mock()

    # Test patch request when patch_integration_settings fails
    mocked_patch_integration_settings.return_value = False
    different_unmapped_card_count = 15

    patch_integration_settings_for_unmapped_cards(workspace_id, different_unmapped_card_count)

    # Verify patch_integration_settings was called
    mocked_patch_integration_settings.assert_called_once_with(
        workspace_id=workspace_id,
        unmapped_card_count=different_unmapped_card_count
    )

    # Verify LastExportDetail was NOT updated when patch fails
    last_export_detail.refresh_from_db()
    assert last_export_detail.unmapped_card_count == new_unmapped_card_count  # Still the old value
