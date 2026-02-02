from enum import Enum

from fyle_accounting_library.rabbitmq.connector import RabbitMQConnection
from fyle_accounting_library.rabbitmq.data_class import RabbitMQData
from fyle_accounting_library.rabbitmq.enums import RabbitMQExchangeEnum


class RoutingKeyEnum(str, Enum):
    """
    Routing key enum
    """
    IMPORT = 'IMPORT.*'
    UTILITY = 'UTILITY.*'
    EXPORT_P0 = 'EXPORT.P0.*'
    EXPORT_P1 = 'EXPORT.P1.*'


class WorkerActionEnum(str, Enum):
    """
    Worker action enum
    """
    DIRECT_EXPORT = 'EXPORT.P0.DIRECT_EXPORT'
    DASHBOARD_SYNC = 'EXPORT.P0.DASHBOARD_SYNC'
    DISABLE_ITEMS = 'IMPORT.DISABLE_ITEMS'
    AUTO_MAP_EMPLOYEES = 'IMPORT.AUTO_MAP_EMPLOYEES'
    CREATE_EXPENSE_GROUP = 'EXPORT.P1.CREATE_EXPENSE_GROUP'
    UPDATE_WORKSPACE_NAME = 'UTILITY.UPDATE_WORKSPACE_NAME'
    EXPENSE_STATE_CHANGE = 'EXPORT.P1.EXPENSE_STATE_CHANGE'
    SYNC_XERO_DIMENSION = 'IMPORT.SYNC_XERO_DIMENSION'
    IMPORT_DIMENSIONS_TO_FYLE = 'IMPORT.IMPORT_DIMENSIONS_TO_FYLE'
    CREATE_ADMIN_SUBSCRIPTION = 'UTILITY.CREATE_ADMIN_SUBSCRIPTION'
    BACKGROUND_SCHEDULE_EXPORT = 'EXPORT.P1.BACKGROUND_SCHEDULE_EXPORT'
    HANDLE_FYLE_REFRESH_DIMENSION = 'IMPORT.HANDLE_FYLE_REFRESH_DIMENSION'
    HANDLE_XERO_REFRESH_DIMENSION = 'IMPORT.HANDLE_XERO_REFRESH_DIMENSION'
    EXPENSE_UPDATED_AFTER_APPROVAL = 'UTILITY.EXPENSE_UPDATED_AFTER_APPROVAL'
    EXPENSE_ADDED_EJECTED_FROM_REPORT = 'UTILITY.EXPENSE_ADDED_EJECTED_FROM_REPORT'
    HANDLE_ORG_SETTING_UPDATED = 'UTILITY.HANDLE_ORG_SETTING_UPDATED'
    CHECK_INTERVAL_AND_SYNC_FYLE_DIMENSION = 'IMPORT.CHECK_INTERVAL_AND_SYNC_FYLE_DIMENSION'
    ADD_ADMINS_TO_WORKSPACE = 'UTILITY.ADD_ADMINS_TO_WORKSPACE'
    CREATE_MISSING_CURRENCY = 'IMPORT.CREATE_MISSING_CURRENCY'
    UPDATE_XERO_SHORT_CODE = 'IMPORT.UPDATE_XERO_SHORT_CODE'


QUEUE_BINDKEY_MAP = {
    'xero_import': RoutingKeyEnum.IMPORT,
    'xero_utility': RoutingKeyEnum.UTILITY,
    'xero_export.p0': RoutingKeyEnum.EXPORT_P0,
    'xero_export.p1': RoutingKeyEnum.EXPORT_P1
}


ACTION_METHOD_MAP = {
    WorkerActionEnum.DIRECT_EXPORT: 'apps.fyle.tasks.import_and_export_expenses',
    WorkerActionEnum.DASHBOARD_SYNC: 'apps.workspaces.actions.export_to_xero',
    WorkerActionEnum.DISABLE_ITEMS: 'fyle_integrations_imports.tasks.disable_items',
    WorkerActionEnum.AUTO_MAP_EMPLOYEES: 'apps.mappings.tasks.async_auto_map_employees',
    WorkerActionEnum.CREATE_EXPENSE_GROUP: 'apps.fyle.tasks.create_expense_groups',
    WorkerActionEnum.EXPENSE_STATE_CHANGE: 'apps.fyle.tasks.import_and_export_expenses',
    WorkerActionEnum.UPDATE_WORKSPACE_NAME: 'apps.workspaces.tasks.update_workspace_name',
    WorkerActionEnum.SYNC_XERO_DIMENSION: 'apps.xero.actions.sync_dimensions',
    WorkerActionEnum.CREATE_ADMIN_SUBSCRIPTION: 'apps.workspaces.tasks.async_create_admin_subscriptions',
    WorkerActionEnum.BACKGROUND_SCHEDULE_EXPORT: 'apps.workspaces.actions.export_to_xero',
    WorkerActionEnum.HANDLE_FYLE_REFRESH_DIMENSION: 'apps.fyle.tasks.sync_dimensions',
    WorkerActionEnum.HANDLE_XERO_REFRESH_DIMENSION: 'apps.xero.actions.refresh_xero_dimension',
    WorkerActionEnum.IMPORT_DIMENSIONS_TO_FYLE: 'apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle',
    WorkerActionEnum.EXPENSE_UPDATED_AFTER_APPROVAL: 'apps.fyle.tasks.update_non_exported_expenses',
    WorkerActionEnum.EXPENSE_ADDED_EJECTED_FROM_REPORT: 'apps.fyle.tasks.handle_expense_report_change',
    WorkerActionEnum.CHECK_INTERVAL_AND_SYNC_FYLE_DIMENSION: 'apps.fyle.tasks.check_interval_and_sync_dimension',
    WorkerActionEnum.ADD_ADMINS_TO_WORKSPACE: 'apps.workspaces.tasks.async_add_admins_to_workspace',
    WorkerActionEnum.CREATE_MISSING_CURRENCY: 'apps.xero.tasks.create_missing_currency',
    WorkerActionEnum.UPDATE_XERO_SHORT_CODE: 'apps.xero.tasks.update_xero_short_code',
    WorkerActionEnum.HANDLE_ORG_SETTING_UPDATED: 'apps.fyle.tasks.handle_org_setting_updated',
}


def get_routing_key(queue_name: str) -> str:
    """
    Get the routing key for a given queue name
    :param queue_name: str
    :return: str
    :raises ValueError: if queue_name is not found in QUEUE_BINDKEY_MAP
    """
    routing_key = QUEUE_BINDKEY_MAP.get(queue_name)
    if routing_key is None:
        raise ValueError(f'Unknown queue name: {queue_name}. Valid queue names are: {list(QUEUE_BINDKEY_MAP.keys())}')
    return routing_key


def publish_to_rabbitmq(payload: dict, routing_key: RoutingKeyEnum) -> None:
    """
    Publish messages to RabbitMQ
    :param: payload: dict
    :param: routing_key: RoutingKeyEnum
    :return: None
    """
    rabbitmq = RabbitMQConnection.get_instance(RabbitMQExchangeEnum.XERO_EXCHANGE)
    data = RabbitMQData(new=payload)
    rabbitmq.publish(routing_key, data)
