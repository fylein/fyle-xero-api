import logging
from django.conf import settings
from apps.fyle.helpers import patch_request
from apps.workspaces.models import FyleCredential, XeroCredentials

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


def patch_integration_settings(workspace_id: int, errors: int = None, is_token_expired = None):
    """
    Patch integration settings
    """

    refresh_token = FyleCredential.objects.get(workspace_id=workspace_id).refresh_token
    url = '{}/integrations/'.format(settings.INTEGRATIONS_SETTINGS_API)
    payload = {
        'tpa_name': 'Fyle Xero Integration',
    }

    if errors is not None:
        payload['errors_count'] = errors

    if is_token_expired is not None:
        payload['is_token_expired'] = is_token_expired

    try:
        patch_request(url, payload, refresh_token)
    except Exception as error:
        logger.error(error, exc_info=True)


def invalidate_xero_credentials(workspace_id):
    xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace_id, is_expired=False, refresh_token__isnull=False).first()
    if xero_credentials:
        if not xero_credentials.is_expired:
            patch_integration_settings(workspace_id, is_token_expired=True)
        xero_credentials.refresh_token = None
        xero_credentials.is_expired = True
        xero_credentials.save()
