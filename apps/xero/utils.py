from django.conf import settings

from xerosdk import XeroSDK

from apps.mappings.models import TenantMapping
from apps.workspaces.models import XeroCredentials
from fyle_accounting_mappings.models import DestinationAttribute


class XeroConnector:
    """
    Xero utility functions
    """

    def __init__(self, credentials_object: XeroCredentials, workspace_id: int):
        client_id = settings.XERO_CLIENT_ID
        client_secret = settings.XERO_CLIENT_SECRET
        base_url = settings.XERO_BASE_URL

        self.connection = XeroSDK(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=credentials_object.refresh_token
        )

        self.workspace_id = workspace_id

        credentials_object.refresh_token = self.connection.refresh_token
        credentials_object.save()

        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)  # Have a bug here will fix this

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

    def sync_tenants(self):
        """
        sync xero tenants
        """
        tenants = self.connection.tenants.get_all()

        tenant_attributes = []

        for tenant in tenants:
            tenant_attributes.append({
                'attribute_type': 'TENANT',
                'display_name': 'Tenant',
                'value': tenant['tenantName'],
                'destination_id': tenant['tenantId']
            })

        tenant_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            tenant_attributes, self.workspace_id)
        return tenant_attributes

    def sync_accounts(self, account_type: str):
        """
        Get accounts
        """
        accounts = self.connection.accounts.get_all()

        accounts = list(filter(lambda current_account: current_account['Type'] == account_type, accounts))

        account_attributes = []

        if account_type == 'BANK':
            attribute_type = 'BANK_ACCOUNT'
            display_name = 'Bank Account'
        else:
            attribute_type = 'ACCOUNT'
            display_name = 'Account'

        for account in accounts:
            account_attributes.append({
                'attribute_type': attribute_type,
                'display_name': display_name,
                'value': account['Name'],
                'destination_id': account['Id']
            })

        account_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            account_attributes, self.workspace_id)
        return account_attributes

    def sync_contacts(self):
        """
        Get contacts
        """
        contacts = self.connection.contacts.get_all()['Contacts']

        contact_attributes = []

        for contact in contacts:
            contact_attributes.append({
                'attribute_type': 'CONTACT',
                'display_name': 'Contact',
                'value': contact['Name'],
                'destination_id': contact['ContactID']
            })

        contact_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            contact_attributes, self.workspace_id)
        return contact_attributes

    def sync_tracking_categories(self):
        """
        Get Tracking Categories
        """
        tracking_categories = self.connection.tracking_categories.get_all()

        tracking_category_attributes = []

        for tracking_category in tracking_categories:
            count = 1
            for option in tracking_category['Options']:
                tracking_category_attributes.append({
                    'attribute_type': tracking_category['Name'].upper().replace(' ', '_'),
                    'display_name': tracking_category['Name'],
                    'value': option,
                    'source_id': 'tracking_category.{}.{}'.format(tracking_category['Name'].lower(), count)
                })
                count = count + 1

        tracking_category_attributes = DestinationAttribute.bulk_upsert_destination_attributes(
            tracking_category_attributes, self.workspace_id)

        return tracking_category_attributes

