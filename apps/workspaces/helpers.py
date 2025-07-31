import logging

from django.conf import settings

from apps.fyle.helpers import patch_request
from apps.workspaces.models import FyleCredential, LastExportDetail, XeroCredentials

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get_error_model_path() -> str:
    """
    Get error model path: This is for imports submodule
    :return: str
    """
    return 'apps.tasks.models.Error'


def get_import_configuration_model_path() -> str:
    """
    Get import configuration model path: This is for imports submodule
    :return: str
    """
    return 'apps.workspaces.models.WorkspaceGeneralSettings'


def get_app_name() -> str:
    """
    Get Integration Name. This is for imports submodule
    :return: str
    """
    return 'XERO'


def patch_integration_settings(workspace_id: int, errors: int = None, is_token_expired = None, unmapped_card_count: int = None):
    """
    Patch integration settings
    """

    fyle_credential = FyleCredential.objects.get(workspace_id=workspace_id)
    refresh_token = fyle_credential.refresh_token
    url = '{}/integrations/'.format(settings.INTEGRATIONS_SETTINGS_API)
    payload = {
        'tpa_name': 'Fyle Xero Integration',
    }

    if errors is not None:
        payload['errors_count'] = errors

    if is_token_expired is not None:
        payload['is_token_expired'] = is_token_expired

    if unmapped_card_count is not None:
        payload['unmapped_card_count'] = unmapped_card_count

    try:
        if fyle_credential.workspace.onboarding_state == 'COMPLETE':
            patch_request(url, payload, refresh_token)
            return True
    except Exception as error:
        logger.error(error, exc_info=True)
        return False


def patch_integration_settings_for_unmapped_cards(workspace_id: int, unmapped_card_count: int) -> None:
    """
    Patch integration settings for unmapped cards
    :param workspace_id: Workspace id
    :param unmapped_card_count: Unmapped card count
    return: None
    """
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)
    if unmapped_card_count != last_export_detail.unmapped_card_count:
        is_patched = patch_integration_settings(workspace_id=workspace_id, unmapped_card_count=unmapped_card_count)
        if is_patched:
            last_export_detail.unmapped_card_count = unmapped_card_count
            last_export_detail.save(update_fields=['unmapped_card_count', 'updated_at'])


def invalidate_xero_credentials(workspace_id):
    xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace_id, is_expired=False, refresh_token__isnull=False).first()
    if xero_credentials:
        if not xero_credentials.is_expired:
            patch_integration_settings(workspace_id, is_token_expired=True)
        xero_credentials.refresh_token = None
        xero_credentials.is_expired = True
        xero_credentials.save()
