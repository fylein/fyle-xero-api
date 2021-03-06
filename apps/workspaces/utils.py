import json
import base64
from typing import Dict

import requests

from django.conf import settings

from future.moves.urllib.parse import urlencode

from xerosdk import InvalidTokenError, InternalServerError

from apps.mappings.tasks import schedule_categories_creation, schedule_auto_map_employees
from apps.xero.tasks import schedule_payment_creation, schedule_xero_objects_status_sync, schedule_reimbursements_sync
from fyle_xero_api.utils import assert_valid
from .models import WorkspaceGeneralSettings


def generate_xero_refresh_token(authorization_code: str) -> str:
    """
    Generate Xero refresh token from authorization code
    """
    api_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': settings.XERO_REDIRECT_URI
    }

    auth = '{0}:{1}'.format(settings.XERO_CLIENT_ID, settings.XERO_CLIENT_SECRET)
    auth = base64.b64encode(auth.encode('utf-8'))

    request_header = {
        'Accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic {0}'.format(
            str(auth.decode())
        )
    }

    token_url = settings.XERO_TOKEN_URI
    response = requests.post(url=token_url, data=urlencode(api_data), headers=request_header)

    if response.status_code == 200:
        return json.loads(response.text)['refresh_token']

    elif response.status_code == 401:
        raise InvalidTokenError('Wrong client secret or/and refresh token', response.text)

    elif response.status_code == 500:
        raise InternalServerError('Internal server error', response.text)


def create_or_update_general_settings(general_settings_payload: Dict, workspace_id):
    """
    Create or update general settings
    :param workspace_id:
    :param general_settings_payload: general settings payload
    :return:
    """
    assert_valid(
        'reimbursable_expenses_object' in general_settings_payload and general_settings_payload[
            'reimbursable_expenses_object'], 'reimbursable_expenses_object field is blank')

    assert_valid('auto_map_employees' in general_settings_payload, 'auto_map_employees field is missing')

    if general_settings_payload['auto_map_employees']:
        assert_valid(general_settings_payload['auto_map_employees'] in ['EMAIL', 'NAME', 'EMPLOYEE_CODE'],
                     'auto_map_employees can have only EMAIL / NAME / EMPLOYEE_CODE')

    general_settings, _ = WorkspaceGeneralSettings.objects.update_or_create(
        workspace_id=workspace_id,
        defaults={
            'reimbursable_expenses_object': general_settings_payload['reimbursable_expenses_object'],
            'corporate_credit_card_expenses_object':
                general_settings_payload['corporate_credit_card_expenses_object']
                if 'corporate_credit_card_expenses_object' in general_settings_payload
                and general_settings_payload['corporate_credit_card_expenses_object'] else None,
            'sync_fyle_to_xero_payments': general_settings_payload['sync_fyle_to_xero_payments'],
            'sync_xero_to_fyle_payments': general_settings_payload['sync_xero_to_fyle_payments'],
            'import_categories': general_settings_payload['import_categories'],
            'auto_map_employees': general_settings_payload['auto_map_employees'],
            'auto_create_destination_entity': general_settings_payload['auto_create_destination_entity']
        }
    )

    schedule_payment_creation(general_settings.sync_fyle_to_xero_payments, workspace_id)

    schedule_xero_objects_status_sync(
        sync_xero_to_fyle_payments=general_settings.sync_xero_to_fyle_payments,
        workspace_id=workspace_id
    )

    schedule_reimbursements_sync(
        sync_xero_to_fyle_payments=general_settings.sync_xero_to_fyle_payments,
        workspace_id=workspace_id
    )

    schedule_categories_creation(import_categories=general_settings.import_categories, workspace_id=workspace_id)

    schedule_auto_map_employees(general_settings_payload['auto_map_employees'], workspace_id)
    
    return general_settings
