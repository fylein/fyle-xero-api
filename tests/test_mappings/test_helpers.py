from unittest import mock

import pytest
from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.helpers import patch_corporate_card_integration_settings
from apps.mappings.schedules import new_schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import WorkspaceGeneralSettings


@pytest.fixture
def configuration(db):
    return WorkspaceGeneralSettings(workspace_id=1, import_categories=False)


@pytest.fixture
def mapping_settings():
    mapping_setting = [
        {
            "source_field": "CATEGORY",
            "workspace_id": 1,
            "import_to_fyle": True
        },
        {
            "source_field": "PROJECT",
            "workspace_id": 1,
            "import_to_fyle": False
        }
    ]

    return mapping_setting


def test_schedule_or_delete_fyle_import_tasks_with_no_configuration(configuration, mapping_settings):
    new_schedule_or_delete_fyle_import_tasks(configuration, mapping_settings)


def test_schedule_or_delete_fyle_import_tasks_with_import_categories(configuration, mapping_settings):
    configuration.import_categories = True
    new_schedule_or_delete_fyle_import_tasks(configuration, mapping_settings)


def test_schedule_or_delete_fyle_import_tasks_with_project_mapping(configuration, mapping_settings):
    project_mapping = MappingSetting.objects.create(
        source_field="PROJECT", workspace_id=1, import_to_fyle=True
    )
    configuration.import_categories = False
    new_schedule_or_delete_fyle_import_tasks(configuration, mapping_settings)
    project_mapping.delete()


@pytest.mark.django_db()
def test_patch_corporate_card_integration_settings(test_connection):
    """
    Test patch_corporate_card_integration_settings helper - tests all conditions
    """
    workspace_id = 1
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    workspace_general_settings.corporate_credit_card_expenses_object = 'BANK TRANSACTION'
    workspace_general_settings.save()

    with mock.patch('apps.mappings.helpers.patch_integration_settings_for_unmapped_cards') as mock_patch:
        patch_corporate_card_integration_settings(workspace_id=workspace_id)
        mock_patch.assert_called_once()
        assert mock_patch.call_args[1]['workspace_id'] == workspace_id
        assert 'unmapped_card_count' in mock_patch.call_args[1]

    # Test that patch is NOT called for non-card expense types
    workspace_general_settings.corporate_credit_card_expenses_object = 'PURCHASE BILL'
    workspace_general_settings.save()

    with mock.patch('apps.mappings.helpers.patch_integration_settings_for_unmapped_cards') as mock_patch:
        patch_corporate_card_integration_settings(workspace_id=workspace_id)
        mock_patch.assert_not_called()
