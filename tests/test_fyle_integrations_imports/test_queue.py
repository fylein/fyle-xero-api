from fyle_integrations_imports.queues import chain_import_fields_to_fyle
from fyle_integrations_imports.dataclasses import TaskSetting


def test_chain_import_fields_to_fyle(mocker):
    mocker.patch('fyle_integrations_imports.tasks.trigger_import_via_schedule')
    mock_chain = mocker.patch('fyle_integrations_imports.queues.Chain')
    mock_chain.return_value.length().__gt__.return_value = 1

    task_settings: TaskSetting = {
        'sdk_connection_string': 'sdk_connection_string',
        'credentials': 'credentials',
        'custom_properties': {
            'func': 'fyle_integrations_imports.tasks.trigger_import_via_schedule',
            'args': {
                'workspace_id': 1,
                'destination_field': 'CUSTOM_FIELD',
                'object_type': 'CUSTOM_FIELD',
                'destination_sync_methods': ['destination_sync_methods'],
                'is_auto_sync_enabled': False,
                'is_3d_mapping': False,
            }
        },
        'import_categories': {
            'destination_field': 'CATEGORY',
            'destination_sync_methods': ['destination_sync_methods'],
            'is_auto_sync_enabled': True,
            'is_3d_mapping': False,
            'charts_of_accounts': 'charts_of_accounts'
        },
        'import_tax': {
            'destination_field': 'TAX_GROUP',
            'destination_sync_methods': ['destination_sync_methods'],
            'is_auto_sync_enabled': False,
            'is_3d_mapping': False
        },
        'import_vendors_as_merchants': {
            'destination_field': 'MERCHANT',
            'destination_sync_methods': ['destination_sync_methods'],
            'is_auto_sync_enabled': False,
            'is_3d_mapping': False
        },
        'mapping_settings': [
            {
                'source_field': 'source_field',
                'destination_field': 'destination_field',
                'is_3d_mapping': False,
                'destination_sync_methods': ['destination_sync_methods'],
                'is_custom': False
            }
        ],
        "import_items": {
            "destination_field": "CATEGORY",
            "destination_sync_methods": ["destination_sync_methods"],
            "is_auto_sync_enabled": True,
            "is_3d_mapping": False
        }
    }

    chain_import_fields_to_fyle(1, task_settings)
