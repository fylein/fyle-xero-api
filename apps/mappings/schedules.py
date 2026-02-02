from datetime import datetime
from typing import Dict, List

from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting

from apps.workspaces.models import WorkspaceGeneralSettings


def new_schedule_or_delete_fyle_import_tasks(
    workspace_general_settings_instance: WorkspaceGeneralSettings,
    mapping_settings: List[Dict]
):
    """
    Schedule or delete fyle import tasks based on the
    workspace general settings and mapping settings
    :param workspace_general_settings_instance: WorkspaceGeneralSettings instance
    :param mapping_settings: List of mapping settings
    :return: None
    """
    # short-hand notation, it returns True as soon as it encounters import_to_fyle as True
    task_to_be_scheduled = any(mapping_setting['import_to_fyle'] for mapping_setting in mapping_settings)

    if (
        task_to_be_scheduled
        or workspace_general_settings_instance.import_customers
        or workspace_general_settings_instance.import_tax_codes
        or workspace_general_settings_instance.import_categories
        or workspace_general_settings_instance.import_suppliers_as_merchants
    ):
        Schedule.objects.update_or_create(
            func='apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle',
            args='{}'.format(workspace_general_settings_instance.workspace_id),
            defaults={
                'schedule_type':Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': datetime.now()
            }
        )
    else:
        import_fields_count = MappingSetting.objects.filter(
            workspace_id=workspace_general_settings_instance.workspace_id,
            import_to_fyle=True
        ).count()

        # if there are no import fields, delete the schedule
        if import_fields_count == 0:
            Schedule.objects.filter(
                func='apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle',
                args='{}'.format(workspace_general_settings_instance.workspace_id)
            ).delete()
