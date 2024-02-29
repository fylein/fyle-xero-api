from datetime import datetime

from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting

from apps.fyle.enums import FyleAttributeEnum
from apps.workspaces.models import WorkspaceGeneralSettings


def schedule_or_delete_fyle_import_tasks(configuration: WorkspaceGeneralSettings):
    """
    :param configuration: WorkspaceGeneralSettings Instance
    :return: None
    """
    project_mapping = MappingSetting.objects.filter(
        source_field=FyleAttributeEnum.PROJECT, workspace_id=configuration.workspace_id
    ).first()
    if (
        configuration.import_categories
        or (project_mapping and project_mapping.import_to_fyle)
        or configuration.import_suppliers_as_merchants
    ):
        start_datetime = datetime.now()
        Schedule.objects.update_or_create(
            func="apps.mappings.tasks.auto_import_and_map_fyle_fields",
            cluster='import',
            args="{}".format(configuration.workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": start_datetime,
            },
        )
    elif (
        not configuration.import_categories
        and not (project_mapping and project_mapping.import_to_fyle)
        and not configuration.import_suppliers_as_merchants
    ):
        Schedule.objects.filter(
            func="apps.mappings.tasks.auto_import_and_map_fyle_fields",
            args="{}".format(configuration.workspace_id),
        ).delete()


def is_auto_sync_allowed(workspace_general_settings: WorkspaceGeneralSettings, mapping_setting: MappingSetting = None):
    """
    Get the auto sync permission
    :return: bool
    """
    is_auto_sync_status_allowed = False
    if (mapping_setting and mapping_setting.destination_field == 'CUSTOMER' and mapping_setting.source_field == 'PROJECT') or workspace_general_settings.import_categories:
        is_auto_sync_status_allowed = True

    return is_auto_sync_status_allowed
