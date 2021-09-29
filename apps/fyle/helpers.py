import logging
from typing import List

from sentry_sdk import capture_message

from apps.workspaces.models import Workspace, FyleCredential

from .utils import FyleConnector

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get_or_store_cluster_domain(workspace_id: int) -> str:
    """
    Get or store cluster domain.
    """
    workspace = Workspace.objects.get(pk=workspace_id)
    if not workspace.cluster_domain:
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        fyle_connector = FyleConnector(fyle_credentials.refresh_token)
        cluster_domain = fyle_connector.get_cluster_domain()['cluster_domain']
        workspace.cluster_domain = cluster_domain
        workspace.save()

    return workspace.cluster_domain


def compare_tpa_and_platform_expenses(tpa_expenses: List[dict], platform_expenses: List[dict], workspace_id: int):
    """
    Compare TPA expenses and platform expenses.
    """
    if len(tpa_expenses) != len(platform_expenses):
        # POST to sentry
        logger.error('count is different {} - {}'.format(len(tpa_expenses), len(platform_expenses)))
        capture_message(
            'PLATFORM MIGRATION\nCount is different - {} - {}\nWorkspace ID - {}'.format(
                len(tpa_expenses), len(platform_expenses), workspace_id
            )
        )
    tpa_expenses_ids = [expense['id'] for expense in tpa_expenses]
    platform_expenses_ids = [expense['id'] for expense in platform_expenses]

    missed_expense_ids = list(set(tpa_expenses_ids).difference(platform_expenses_ids))
    if missed_expense_ids:
        # POST to sentry
        capture_message('PLATFORM MIGRATION\nMissed_expense_ids - {}\nWorkspace ID - {}'.format(
            missed_expense_ids, workspace_id
        ))
        logger.error('missed_expense_ids {}'.format(missed_expense_ids))
