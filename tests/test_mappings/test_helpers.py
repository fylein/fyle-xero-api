import pytest
from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.helpers import schedule_or_delete_fyle_import_tasks
from apps.workspaces.models import WorkspaceGeneralSettings


@pytest.fixture
def configuration(db):
    return WorkspaceGeneralSettings(workspace_id=1, import_categories=False)


def test_schedule_or_delete_fyle_import_tasks_with_no_configuration(configuration):
    schedule_or_delete_fyle_import_tasks(configuration)


def test_schedule_or_delete_fyle_import_tasks_with_import_categories(configuration, db):
    configuration.import_categories = True
    schedule_or_delete_fyle_import_tasks(configuration)


def test_schedule_or_delete_fyle_import_tasks_with_project_mapping(configuration, db):
    project_mapping = MappingSetting.objects.create(
        source_field="PROJECT", workspace_id=1, import_to_fyle=True
    )
    configuration.import_categories = False
    schedule_or_delete_fyle_import_tasks(configuration)
    project_mapping.delete()
