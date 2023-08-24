from fyle_accounting_mappings.models import ExpenseAttribute
from django.db.models import Q

from apps.tasks.models import TaskLog
from apps.workspaces.models import FyleCredential, WorkspaceGeneralSettings, Workspace
from apps.workspaces.serializers import WorkspaceSerializer
from datetime import datetime, timezone
from .models import Expense, ExpenseGroup, ExpenseGroupSettings

from fyle_integrations_platform_connector import PlatformConnector

def get_expense_field(workspace_id):

    default_attributes = ['EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER', 'CORPORATE_CARD', 'TAX_GROUP']
    attributes = ExpenseAttribute.objects.filter(
        ~Q(attribute_type__in=default_attributes),
        workspace_id=workspace_id
    ).values('attribute_type', 'display_name').distinct()

    expense_fields= [
        {'attribute_type': 'COST_CENTER', 'display_name': 'Cost Center'},
        {'attribute_type': 'PROJECT', 'display_name': 'Project'}
    ]

    for attribute in attributes:
        expense_fields.append(attribute)
    
    return expense_fields


def sync_fyle_dimension(workspace_id):

    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.source_synced_at:
        time_interval = datetime.now(timezone.utc) - workspace.source_synced_at

    if workspace.source_synced_at is None or time_interval.days > 0:
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

        platform = PlatformConnector(fyle_credentials)
        platform.import_fyle_dimensions()

        workspace.source_synced_at = datetime.now()
        workspace.save(update_fields=['source_synced_at'])


def refresh_fyle_dimension(workspace_id):

    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentials)
    platform.import_fyle_dimensions()

    workspace = Workspace.objects.get(id=workspace_id)
    workspace.source_synced_at = datetime.now()
    workspace.save(update_fields=['source_synced_at'])


def exportable_expense_group(workspace_id):

    configuration = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    fund_source = []

    if configuration.reimbursable_expenses_object:
        fund_source.append('PERSONAL')
    if configuration.corporate_credit_card_expenses_object:
        fund_source.append('CCC')

    expense_group_ids = ExpenseGroup.objects.filter(
        workspace_id=workspace_id,
        exported_at__isnull=True,
        fund_source__in=fund_source
    ).values_list('id', flat=True)

    return expense_group_ids
