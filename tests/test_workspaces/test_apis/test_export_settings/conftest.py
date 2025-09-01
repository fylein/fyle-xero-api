import pytest
from datetime import datetime, timezone

from apps.fyle.models import ExpenseGroup, ExpenseGroupSettings
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import Error, TaskLog
from apps.workspaces.models import LastExportDetail, Workspace, WorkspaceGeneralSettings
from fyle_accounting_mappings.models import ExpenseAttribute


@pytest.fixture
def setup_test_data_for_export_settings(db):
    """
    Setup test data for export settings tests
    """
    def _setup_test_data_for_export_settings(workspace_id, config=None):
        workspace, _ = Workspace.objects.get_or_create(
            id=workspace_id,
            defaults={
                'name': f'Test Workspace {workspace_id}',
                'fyle_org_id': f'test_org_{workspace_id}',
                'xero_short_code': f'xero_{workspace_id}',
                'last_synced_at': None,
                'source_synced_at': None,
                'destination_synced_at': None,
                'xero_accounts_last_synced_at': datetime.now(tz=timezone.utc),
                'created_at': datetime.now(tz=timezone.utc),
                'updated_at': datetime.now(tz=timezone.utc),
            }
        )

        LastExportDetail.objects.get_or_create(
            workspace=workspace,
            defaults={
                'last_exported_at': None,
                'export_mode': None,
                'total_expense_groups_count': 0,
                'successful_expense_groups_count': 0,
                'failed_expense_groups_count': 0,
            }
        )

        if config:
            WorkspaceGeneralSettings.objects.get_or_create(
                workspace_id=workspace_id,
                defaults={
                    'reimbursable_expenses_object': config.get('reimbursable_expenses_object', 'EXPENSE'),
                    'corporate_credit_card_expenses_object': config.get('corporate_credit_card_expenses_object', 'CREDIT CARD PURCHASE'),
                    'auto_map_employees': 'EMAIL',
                    'auto_create_destination_entity': True,
                    'auto_create_merchant_destination_entity': False,
                    'map_merchant_to_contact': False,
                    'import_categories': True,
                    'import_tax_codes': False,
                    'import_customers': False,
                    'import_suppliers_as_merchants': False,
                }
            )
        else:
            WorkspaceGeneralSettings.objects.get_or_create(
                workspace_id=workspace_id,
                defaults={
                    'reimbursable_expenses_object': 'EXPENSE',
                    'corporate_credit_card_expenses_object': 'CREDIT CARD PURCHASE',
                    'auto_map_employees': 'EMAIL',
                    'auto_create_destination_entity': True,
                    'auto_create_merchant_destination_entity': False,
                    'map_merchant_to_contact': False,
                    'import_categories': True,

                    'import_tax_codes': False,
                    'import_customers': False,
                    'import_suppliers_as_merchants': False,
                }
            )

        ExpenseGroupSettings.objects.get_or_create(
            workspace_id=workspace_id,
            defaults={
                'reimbursable_expense_group_fields': ['fund_source', 'report_id', 'employee_email', 'claim_number'],
                'corporate_credit_card_expense_group_fields': ['fund_source', 'employee_email', 'claim_number', 'expense_id', 'report_id'],
                'expense_state': 'PAYMENT_PROCESSING',
                'reimbursable_expense_state': 'PAYMENT_PROCESSING',
                'ccc_expense_state': 'PAYMENT_PROCESSING',
                'reimbursable_export_date_type': 'current_date',
                'ccc_export_date_type': 'spent_at',
                'split_expense_grouping': 'MULTIPLE_LINE_ITEM',
            }
        )

        TaskLog.objects.get_or_create(
            workspace_id=workspace_id,
            type=TaskLogTypeEnum.CREATING_BANK_TRANSACTION,
            defaults={
                'status': TaskLogStatusEnum.ENQUEUED,
                'task_id': f'CREATING_BANK_TRANSACTION_{workspace_id}',
            }
        )

        return workspace

    return _setup_test_data_for_export_settings


@pytest.fixture
def create_expense_groups(db):
    """
    Create expense groups for testing
    """
    def _create_expense_groups(workspace_id, expense_group_configs):
        expense_groups = []
        for config in expense_group_configs:
            expense_group = ExpenseGroup.objects.create(
                id=config['id'],
                workspace_id=workspace_id,
                fund_source=config['fund_source'],
                description={
                    'employee_email': f'employee{config["id"]}@example.com',
                    'report_id': f'rp{config["id"]}',
                    'claim_number': f'C/{config["id"]}',
                    'settlement_id': f'set{config["id"]}',
                    'fund_source': config['fund_source']
                },
                response_logs=None,
                exported_at=config.get('exported_at'),
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
            expense_groups.append(expense_group)
        return expense_groups

    return _create_expense_groups


@pytest.fixture
def create_mapping_errors(db):
    """
    Create mapping errors for testing
    """
    def _create_mapping_errors(workspace_id, error_configs):
        errors = []
        for config in error_configs:
            if config['type'] in ['EMPLOYEE_MAPPING', 'CATEGORY_MAPPING']:
                ExpenseAttribute.objects.get_or_create(
                    workspace_id=workspace_id,
                    attribute_type=config['attribute_type'],
                    display_name=config['display_name'],
                    value=config['value'],
                    defaults={
                        'source_id': f'src_{config["value"]}',
                        'active': True,
                        'detail': {
                            'full_name': config['value'],
                            'email': config['value'] if config['attribute_type'] == 'EMPLOYEE' else None
                        }
                    }
                )

            error = Error.objects.create(
                workspace_id=workspace_id,
                type=config['type'],
                error_title=config['error_title'],
                error_detail=config['error_detail'],
                expense_group_id=config.get('expense_group_id'),
                is_resolved=config.get('is_resolved', False),
                repetition_count=1,
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )

            if config['type'] in ['EMPLOYEE_MAPPING', 'CATEGORY_MAPPING']:
                error.mapping_error_expense_group_ids = config['mapping_error_expense_group_ids']
                error.save()

            errors.append(error)
        return errors

    return _create_mapping_errors


@pytest.fixture
def create_task_logs(db):
    """
    Create task logs for testing
    """
    def _create_task_logs(workspace_id, task_log_configs):
        task_logs = []
        for config in task_log_configs:
            task_log = TaskLog.objects.create(
                workspace_id=workspace_id,
                type=config['type'],
                status=config['status'],
                expense_group_id=config.get('expense_group_id'),
                task_id=f'{config["type"]}_{workspace_id}_{config.get("expense_group_id", "")}',
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
            task_logs.append(task_log)
        return task_logs

    return _create_task_logs
