from datetime import datetime

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
        'custom_properties': None
    }

    ALLOWED_SOURCE_FIELDS = [
        FyleAttributeEnum.PROJECT,
        FyleAttributeEnum.COST_CENTER,
    ]

    if workspace_general_settings.import_tax_codes:
        task_settings['import_tax'] = {
            'destination_field': 'TAX_CODE',
            'destination_sync_methods': [SYNC_METHODS['TAX_CODE']],
            'is_auto_sync_enabled': False,
            'is_3d_mapping': False
        }

    if workspace_general_settings.import_categories:
        task_settings['import_categories'] = {
            'destination_field': 'ACCOUNT',
            'destination_sync_methods': [SYNC_METHODS['ACCOUNT']],
            'is_auto_sync_enabled': True,
            'is_3d_mapping': False,
            'charts_of_accounts': workspace_general_settings.charts_of_accounts
        }

    if workspace_general_settings.import_suppliers_as_merchants:
        task_settings['custom_properties'] = {
            'func': 'apps.mappings.tasks.auto_create_suppliers_as_merchants',
            'args': {
                'workspace_id': workspace_id
            }
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
