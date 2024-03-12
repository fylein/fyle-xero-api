import pytest
from fyle_accounting_mappings.models import MappingSetting

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
