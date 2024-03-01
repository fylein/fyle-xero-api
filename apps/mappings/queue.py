from datetime import datetime, timedelta

from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting
from apps.fyle.enums import FyleAttributeEnum
from apps.mappings.constants import SYNC_METHODS
from apps.mappings.helpers import is_auto_sync_allowed
from fyle_integrations_imports.dataclasses import TaskSetting
from fyle_integrations_imports.queues import chain_import_fields_to_fyle
from apps.workspaces.models import WorkspaceGeneralSettings, XeroCredentials


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: str):
    if employee_mapping_preference:
        Schedule.objects.update_or_create(
            func="apps.mappings.tasks.async_auto_map_employees",
            cluster='import',
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.async_auto_map_employees",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_cost_centers_creation(import_to_fyle, workspace_id: int):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.mappings.tasks.auto_create_cost_center_mappings",
            cluster='import',
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.auto_create_cost_center_mappings",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_tax_groups_creation(import_tax_codes, workspace_id):
    if import_tax_codes:
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.mappings.tasks.auto_create_tax_codes_mappings",
            cluster='import',
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.auto_create_tax_codes_mappings",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_fyle_attributes_creation(workspace_id: int):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()

    if mapping_settings:
        schedule, _ = Schedule.objects.get_or_create(
            func="apps.mappings.tasks.async_auto_create_custom_field_mappings",
            cluster='import',
            args="{0}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now() + timedelta(hours=24),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.async_auto_create_custom_field_mappings",
            args=workspace_id,
        ).first()

        if schedule:
            schedule.delete()


def construct_tasks_and_chain_import_fields_to_fyle(workspace_id: int):
    """
    Construct tasks and chain import fields to fyle
    :param workspace_id: Workspace Id
    """
    mapping_settings = MappingSetting.objects.filter(
        workspace_id=workspace_id,
        import_to_fyle=True
    )
    workspace_general_settings = WorkspaceGeneralSettings.objects.get(
        workspace_id=workspace_id
    )
    credentials = XeroCredentials.objects.get(
        workspace_id=workspace_id
    )

    # import_vendors_as_merchants is not used in xero, placeholder to avoid KeyError
    task_settings: TaskSetting = {
        'import_tax': None,
        'import_vendors_as_merchants': None,
        'import_suppliers_as_merchants': None,
        'import_categories': None,
        'import_items': None,
        'mapping_settings': [],
        'credentials': credentials,
        'sdk_connection_string': 'apps.xero.utils.XeroConnector',
    }

    # For now adding only for PROJECT
    ALLOWED_SOURCE_FIELDS = [
        FyleAttributeEnum.PROJECT,
        FyleAttributeEnum.COST_CENTER,
    ]

    if workspace_general_settings.import_tax_codes:
        task_settings['import_tax'] = {
            'destination_field': 'TAX_CODE',
            'destination_sync_methods': [SYNC_METHODS['TAX_CODE']],
            'is_auto_sync_enabled': is_auto_sync_allowed(workspace_general_settings, None),
            'is_3d_mapping': False
        }

    if workspace_general_settings.import_categories:
        task_settings['import_categories'] = {
            'destination_field': 'ACCOUNT',
            'destination_sync_methods': [SYNC_METHODS['ACCOUNT']],
            'is_auto_sync_enabled': is_auto_sync_allowed(workspace_general_settings, None),
            'is_3d_mapping': False,
            'charts_of_accounts': workspace_general_settings.charts_of_accounts
        }

    if mapping_settings:
        for mapping_setting in mapping_settings:
            if mapping_setting.source_field in ALLOWED_SOURCE_FIELDS or mapping_setting.is_custom:
                task_settings['mapping_settings'].append(
                    {
                        'source_field': mapping_setting.source_field,
                        'destination_field': mapping_setting.destination_field,
                        'is_custom': mapping_setting.is_custom,
                        'destination_sync_methods': [SYNC_METHODS.get(mapping_setting.destination_field.upper(), 'tracking_categories')],
                        'is_auto_sync_enabled': is_auto_sync_allowed(workspace_general_settings, mapping_setting)
                    }
                )

    chain_import_fields_to_fyle(workspace_id, task_settings)
