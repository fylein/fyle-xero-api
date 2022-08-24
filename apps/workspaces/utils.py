import json
import base64
from typing import Dict
import datetime

import requests
import jwt

from django.conf import settings

from future.moves.urllib.parse import urlencode

from xerosdk import InvalidTokenError, InternalServerError, XeroSDK

from fyle_accounting_mappings.models import MappingSetting

from apps.mappings.tasks import schedule_categories_creation, schedule_auto_map_employees, schedule_tax_groups_creation, \
    schedule_xero_contacts_creation
from apps.xero.tasks import schedule_payment_creation, schedule_xero_objects_status_sync, schedule_reimbursements_sync

from fyle_xero_api.utils import assert_valid
from .models import WorkspaceGeneralSettings, Workspace
from ..fyle.models import ExpenseGroupSettings


def generate_token(authorization_code: str, redirect_uri: str = None) -> str:
    api_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': settings.XERO_REDIRECT_URI if not redirect_uri else redirect_uri
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
    return response


def revoke_token(refresh_token: str) -> None:
    """
    Revoke token
    """
    api_data = {
        'token': refresh_token
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

    revocation_url = settings.XERO_TOKEN_URI.replace('/token', '/revocation')

    requests.post(url=revocation_url, data=urlencode(api_data), headers=request_header)


def generate_xero_refresh_token(authorization_code: str) -> str:
    """
    Generate Xero refresh token from authorization code
    """
    response = generate_token(authorization_code)

    if response.status_code == 200:
        successful_response = json.loads(response.text)
        return successful_response['refresh_token']


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

    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()
    workspace = Workspace.objects.filter(id=workspace_id).first()
    map_merchant_to_contact = True

    if workspace_general_settings:
        map_merchant_to_contact = workspace_general_settings.map_merchant_to_contact

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
            'import_tax_codes': general_settings_payload['import_tax_codes'] if 'import_tax_codes' in general_settings_payload else False,
            'import_categories': general_settings_payload['import_categories'],
            'auto_map_employees': general_settings_payload['auto_map_employees'],
            'auto_create_destination_entity': general_settings_payload['auto_create_destination_entity'],
            'auto_create_merchant_destination_entity': general_settings_payload['auto_create_merchant_destination_entity'],
            'map_merchant_to_contact': map_merchant_to_contact,
            'change_accounting_period': general_settings_payload['change_accounting_period'],
            'charts_of_accounts': general_settings_payload['charts_of_accounts'],
            'import_customers': general_settings_payload['import_customers']
        }
    )
    if workspace_general_settings:
        if set(workspace_general_settings.charts_of_accounts) != set(general_settings_payload['charts_of_accounts']):
            workspace.xero_accounts_last_synced_at = None
            workspace.save()

    # Maintaining this flag update_customer_import_settings to update/create Mapping Setting row
    update_customer_import_settings = False
    import_to_fyle = True

    # General Settings exist already and have import_customers enabled and the current setting is disabled
    if not general_settings.import_customers and workspace_general_settings and \
        workspace_general_settings.import_customers is True:
        import_to_fyle = False
        update_customer_import_settings = True

    if general_settings.import_customers or update_customer_import_settings:
        # Signal would take care of syncing them to Fyle
        MappingSetting.objects.update_or_create(
            source_field='PROJECT',
            workspace_id=workspace_id,
            destination_field='CUSTOMER',
            defaults={
                'import_to_fyle': import_to_fyle,
                'is_custom': False
            }
        )

    if general_settings.map_merchant_to_contact and \
            general_settings.corporate_credit_card_expenses_object == 'BANK TRANSACTION':
        expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)

        ccc_expense_group_fields = expense_group_settings.corporate_credit_card_expense_group_fields
        ccc_expense_group_fields.append('expense_id')
        expense_group_settings.corporate_credit_card_expense_group_fields = list(set(ccc_expense_group_fields))
        expense_group_settings.ccc_export_date_type = 'spent_at'

        expense_group_settings.save()

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

    schedule_tax_groups_creation(import_tax_codes=general_settings.import_tax_codes, workspace_id=workspace_id)
    
    schedule_xero_contacts_creation(general_settings.auto_create_merchant_destination_entity, workspace_id)
    return general_settings


def generate_xero_identity(authorization_code: str, redirect_uri: str) -> str:
    """
    Generate Xero identity from authorization code
    """
    response = generate_token(authorization_code, redirect_uri=redirect_uri)

    if response.status_code == 200:
        successful_response = json.loads(response.text)
        decoded_jwt = jwt.decode(successful_response['id_token'], options={"verify_signature": False})

        connection = XeroSDK(
            base_url=settings.XERO_BASE_URL,
            client_id=settings.XERO_CLIENT_ID,
            client_secret=settings.XERO_CLIENT_SECRET,
            refresh_token=successful_response['refresh_token']
        )

        identity = {
            'user': {
                'given_name': decoded_jwt['given_name'],
                'family_name': decoded_jwt['family_name'],
                'email': decoded_jwt['email']
            },
            'tenants': connection.tenants.get_all()
        }

        # Revoke refresh token
        revoke_token(successful_response['refresh_token'])
        return identity

    elif response.status_code == 400:
        raise InvalidTokenError('Invalid Requests, something wrong with request params', response.text)

    elif response.status_code == 401:
        raise InvalidTokenError('Wrong client secret or/and refresh token', response.text)

    elif response.status_code == 500:
        raise InternalServerError('Internal server error', response.text)
