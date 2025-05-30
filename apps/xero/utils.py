import base64
import json
import logging
from datetime import datetime, timedelta
from time import sleep
from typing import Dict, List, Optional

from apps.workspaces.helpers import get_app_name
import unidecode
from fyle_accounting_mappings.models import DestinationAttribute, MappingSetting
from xerosdk import XeroSDK
from xerosdk.exceptions import WrongParamsError

from apps.mappings.models import GeneralMapping, TenantMapping
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.models import BankTransaction, BankTransactionLineItem, Bill, BillLineItem, Payment
from fyle_xero_api import settings

logger = logging.getLogger(__name__)
logger.level = logging.INFO

CHARTS_OF_ACCOUNTS = ["EXPENSE", "ASSET", "EQUITY", "LIABILITY", "REVENUE"]


AttributeDisableCallbackPath = {
    'ACCOUNT': 'fyle_integrations_imports.modules.categories.disable_categories',
    'SUPPLIER': 'fyle_integrations_imports.modules.merchants.disable_merchants',
    'PROJECT': 'fyle_integrations_imports.modules.projects.disable_projects',
    'COST_CENTER': 'fyle_integrations_imports.modules.cost_centers.disable_cost_centers'
}


def format_updated_at(updated_at):
    return datetime.strftime(updated_at, "%Y-%m-%dT%H:%M:%S")


def get_last_synced_at(workspace_id: int, attribute_type: str):
    latest_synced_record = (
        DestinationAttribute.objects.filter(
            workspace_id=workspace_id, attribute_type=attribute_type
        )
        .order_by("-updated_at")
        .first()
    )
    updated_at = (
        format_updated_at(latest_synced_record.updated_at)
        if latest_synced_record
        else None
    )

    return updated_at


class XeroConnector:
    """
    Xero utility functions
    """

    def __init__(self, credentials_object: XeroCredentials, workspace_id: int):
        client_id = settings.XERO_CLIENT_ID
        client_secret = settings.XERO_CLIENT_SECRET
        base_url = settings.XERO_BASE_URL
        refresh_token = credentials_object.refresh_token

        self.connection = XeroSDK(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
        )

        self.workspace_id = workspace_id

        credentials_object.refresh_token = self.connection.refresh_token
        credentials_object.save()

    def is_duplicate_deletion_skipped(self, attribute_type: str, is_tracking_category: bool = False) -> bool:
        """
        Check if duplicate deletion is skipped for the attribute type
        :param attribute_type: Type of the attribute
        :return: Whether deletion is skipped
        """
        if attribute_type in [
            'ACCOUNT', 'SUPPLIER', 'ITEM', 'CUSTOMER', 'CONTACT'
        ] or is_tracking_category:
            return False

        return True

    def is_import_enabled(self, attribute_type: str, is_tracking_category: bool = False) -> bool:
        """
        Check if import is enabled for the attribute type
        :param attribute_type: Type of the attribute
        :return: Whether import is enabled
        """
        is_import_to_fyle_enabled = False

        configuration = WorkspaceGeneralSettings.objects.filter(workspace_id=self.workspace_id).first()
        if not configuration:
            return is_import_to_fyle_enabled

        if attribute_type in ['ACCOUNT'] and configuration.import_categories:
            is_import_to_fyle_enabled = True

        elif attribute_type == 'SUPPLIER' and configuration.import_suppliers_as_merchants:
            is_import_to_fyle_enabled = True

        elif attribute_type == 'CUSTOMER' and configuration.import_customers:
            is_import_to_fyle_enabled = True

        elif attribute_type in ['ITEM'] or is_tracking_category:
            mapping_setting = MappingSetting.objects.filter(workspace_id=self.workspace_id, destination_field=attribute_type).first()
            if mapping_setting and mapping_setting.import_to_fyle:
                is_import_to_fyle_enabled = True

        return is_import_to_fyle_enabled

    def get_attribute_disable_callback_path(self, attribute_type: str) -> Optional[str]:
        """
        Get the attribute disable callback path
        :param attribute_type: Type of the attribute
        :return: attribute disable callback path or none
        """
        if attribute_type in ['ACCOUNT', 'SUPPLIER']:
            return AttributeDisableCallbackPath.get(attribute_type)

        mapping_setting = MappingSetting.objects.filter(
            workspace_id=self.workspace_id,
            destination_field=attribute_type
        ).first()

        if mapping_setting and not mapping_setting.is_custom:
            return AttributeDisableCallbackPath.get(mapping_setting.source_field)

    def sync_suppliers(self):
        """
        Sync Suppliers
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        updated_at = get_last_synced_at(self.workspace_id, "SUPPLIER")

        includeArchived = True if updated_at else False

        params = {
            'where': 'IsSupplier=true',
            'includeArchived': includeArchived
        }

        supplier_generator = self.connection.contacts.list_all_generator(
            modified_after=updated_at, **params
        )

        for suppliers in supplier_generator:
            supplier_attributes = []

            for supplier in suppliers["Contacts"]:
                detail = {
                    "email": supplier["EmailAddress"]
                    if "EmailAddress" in supplier
                    else None
                }
                supplier_attributes.append(
                    {
                        "attribute_type": "SUPPLIER",
                        "display_name": "Supplier",
                        "value": supplier["Name"],
                        "destination_id": supplier["ContactID"],
                        "detail": detail,
                        "active": True if supplier["ContactStatus"] == "ACTIVE" else False,
                    }
                )

            DestinationAttribute.bulk_create_or_update_destination_attributes(
                supplier_attributes, "SUPPLIER", self.workspace_id, True,
                skip_deletion=self.is_duplicate_deletion_skipped(attribute_type='SUPPLIER'),
                app_name=get_app_name(),
                attribute_disable_callback_path=self.get_attribute_disable_callback_path(attribute_type='SUPPLIER'),
                is_import_to_fyle_enabled=self.is_import_enabled(attribute_type='SUPPLIER')
            )
            sleep(1)

        return []

    def get_or_create_contact(
        self, contact_name: str, email: str = None, create: bool = False
    ):
        """
        Call xero api to get or create contact
        :param email: email for contact user
        :param contact_name: Name of the contact
        :param create: False to just Get and True to Get or Create if not exists
        :return: Contact
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        contact_name = contact_name.replace("#", "%23")  # Replace '#' with %23
        contact_name = contact_name.replace(
            '"', ""
        )  # remove double quotes from merchant name
        contact_name = contact_name.replace("&", "")  # remove & merchant name
        split_contact_name = contact_name.split()   # Split contact name by space

        contact_name = ' '.join(split_contact_name)  # Join contact name by space

        contact = self.connection.contacts.search_contact_by_contact_name(contact_name)

        if not contact:
            if create:
                created_contact = self.post_contact(contact_name, email)
                return self.create_contact_destination_attribute(created_contact)
            else:
                return

        else:
            return self.create_contact_destination_attribute(contact)

    def get_organisations(self):
        """
        Get xero organisations
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        return self.connection.organisations.get_all()

    def sync_tenants(self):
        """
        sync xero tenants
        """
        tenants = self.connection.tenants.get_all()

        tenant_attributes = []

        for tenant in tenants:
            tenant_attributes.append(
                {
                    "attribute_type": "TENANT",
                    "display_name": "Tenant",
                    "value": tenant["tenantName"],
                    "destination_id": tenant["tenantId"],
                    "active": True
                }
            )

        tenant_attributes = (
            DestinationAttribute.bulk_create_or_update_destination_attributes(
                tenant_attributes, "TENANT", self.workspace_id, True
            )
        )
        return tenant_attributes

    def get_tax_inclusive_amount(self, amount, default_tax_code_id):
        tax_attribute = DestinationAttribute.objects.filter(
            destination_id=default_tax_code_id,
            attribute_type="TAX_CODE",
            workspace_id=self.workspace_id,
        ).first()
        general_settings = WorkspaceGeneralSettings.objects.get(
            workspace_id=self.workspace_id
        )
        tax_inclusive_amount = amount
        if tax_attribute and general_settings.import_tax_codes:
            tax_rate = float((tax_attribute.detail["tax_rate"]) / 100)
            tax_amount = round((amount - (amount / (tax_rate + 1))), 2)
            tax_inclusive_amount = round((amount - tax_amount), 2)
        return tax_inclusive_amount

    def sync_tax_codes(self):
        """
        Get Tax Codes
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)
        tax_codes = self.connection.tax_rates.get_all()["TaxRates"]

        tax_attributes = []
        for tax_code in tax_codes:
            effective_tax_rate = tax_code["EffectiveRate"]
            if effective_tax_rate >= 0:
                tax_attributes.append(
                    {
                        "attribute_type": "TAX_CODE",
                        "display_name": "Tax Code",
                        "value": "{0} @{1}%".format(
                            tax_code["Name"], effective_tax_rate
                        ),
                        "destination_id": tax_code["TaxType"],
                        "detail": {
                            "tax_rate": effective_tax_rate,
                            "tax_refs": tax_code["TaxComponents"],
                        },
                        "active": True
                    }
                )

        DestinationAttribute.bulk_create_or_update_destination_attributes(
            tax_attributes, "TAX_CODE", self.workspace_id, True
        )

        return []

    def sync_accounts(self):
        """
        Get accounts
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        workspace = Workspace.objects.filter(id=self.workspace_id).first()

        updated_at = get_last_synced_at(self.workspace_id, "ACCOUNT")

        if not workspace.xero_accounts_last_synced_at:
            updated_at = None

        accounts = self.connection.accounts.get_all(modified_after=updated_at)[
            "Accounts"
        ]

        account_attributes = {"bank_account": [], "account": []}

        for account in accounts:
            detail = {
                "account_type": account["Class"],
                "enable_payments_to_account": account["EnablePaymentsToAccount"],
                "active": True if account["Status"] == "ACTIVE" else False,
            }

            if account["Type"] == "BANK":
                account_attributes["bank_account"].append(
                    {
                        "attribute_type": "BANK_ACCOUNT",
                        "display_name": "Bank Account",
                        "value": unidecode.unidecode(
                            "{0}".format(account["Name"])
                        ).replace("/", "-"),
                        "destination_id": account["AccountID"],
                        "active": True if account["Status"] == "ACTIVE" else False,
                        "detail": detail,
                    }
                )

            elif account["Class"] in CHARTS_OF_ACCOUNTS:
                account_attributes["account"].append(
                    {
                        "attribute_type": "ACCOUNT",
                        "display_name": "Account",
                        "value": unidecode.unidecode(
                            "{0}".format(account["Name"])
                        ).replace("/", "-"),
                        "destination_id": account["Code"],
                        "active": True if account["Status"] == "ACTIVE" else False,
                        "detail": detail,
                    }
                )

        for attribute_type, account_attribute in account_attributes.items():
            if account_attribute:
                DestinationAttribute.bulk_create_or_update_destination_attributes(
                    account_attribute, attribute_type.upper(), self.workspace_id, True,
                    skip_deletion=self.is_duplicate_deletion_skipped(attribute_type='ACCOUNT'),
                    app_name=get_app_name(),
                    attribute_disable_callback_path=self.get_attribute_disable_callback_path(attribute_type='ACCOUNT'),
                    is_import_to_fyle_enabled=self.is_import_enabled(attribute_type='ACCOUNT')
                )

        workspace.xero_accounts_last_synced_at = datetime.now()
        workspace.save()

        return []

    def sync_contacts(self):
        """
        Get contacts
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        updated_at = get_last_synced_at(self.workspace_id, "CONTACT")

        params = {
            'where': 'IsCustomer=false',
            'includeArchived': 'true'
        }

        contacts_generator = self.connection.contacts.list_all_generator(
            modified_after=updated_at, **params
        )

        for contacts in contacts_generator:
            contact_attributes = []

            for contact in contacts["Contacts"]:
                detail = {
                    "email": contact["EmailAddress"]
                    if "EmailAddress" in contact
                    else None
                }
                contact_attributes.append(
                    {
                        "attribute_type": "CONTACT",
                        "display_name": "Contact",
                        "value": contact["Name"],
                        "destination_id": contact["ContactID"],
                        "detail": detail,
                        "active": True if contact["ContactStatus"] == "ACTIVE" else False,
                    }
                )

            DestinationAttribute.bulk_create_or_update_destination_attributes(
                contact_attributes, "CONTACT", self.workspace_id, True,
                skip_deletion=self.is_duplicate_deletion_skipped(attribute_type='CONTACT'),
                app_name=get_app_name(),
                attribute_disable_callback_path=self.get_attribute_disable_callback_path(attribute_type='CONTACT'),
                is_import_to_fyle_enabled=self.is_import_enabled(attribute_type='CONTACT')
            )
            sleep(1)

        return []

    def sync_customers(self):
        """
        Get customers
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        params = {
            'where': 'IsCustomer=true',
            'includeArchived': 'true',
        }

        customers_generator = self.connection.contacts.list_all_generator(**params)

        for customers in customers_generator:
            customer_attributes = []

            for customer in customers["Contacts"]:
                customer_attributes.append(
                    {
                        "attribute_type": "CUSTOMER",
                        "display_name": "Customer",
                        "value": customer["Name"],
                        "destination_id": customer["ContactID"],
                        "detail": {
                            "email": customer["EmailAddress"]
                            if "EmailAddress" in customer
                            else None
                        },
                        "active": True if customer["ContactStatus"] == "ACTIVE" else False,
                    }
                )

            DestinationAttribute.bulk_create_or_update_destination_attributes(
                customer_attributes, "CUSTOMER", self.workspace_id, True,
                skip_deletion=self.is_duplicate_deletion_skipped(attribute_type='CUSTOMER'),
                app_name=get_app_name(),
                attribute_disable_callback_path=self.get_attribute_disable_callback_path(attribute_type='CUSTOMER'),
                is_import_to_fyle_enabled=self.is_import_enabled(attribute_type='CUSTOMER')
            )
            sleep(1)

        return []

    def sync_tracking_categories(self):
        """
        Get Tracking Categories
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        tracking_categories = self.connection.tracking_categories.get_all()[
            "TrackingCategories"
        ]

        for tracking_category in tracking_categories:
            tracking_category_attributes = []

            for option in tracking_category["Options"]:
                if tracking_category["Name"].lower() == "customer":
                    tracking_category["Name"] = "{}-TC".format(
                        tracking_category["Name"]
                    )

                tracking_category_attributes.append(
                    {
                        "attribute_type": tracking_category["Name"]
                        .upper()
                        .replace(" ", "_"),
                        "display_name": tracking_category["Name"],
                        "value": option["Name"],
                        "destination_id": option["TrackingOptionID"],
                        "active": True if option["Status"] == "ACTIVE" else False,
                    }
                )

            DestinationAttribute.bulk_create_or_update_destination_attributes(
                tracking_category_attributes,
                tracking_category["Name"].upper().replace(" ", "_"),
                self.workspace_id,
                True,
                skip_deletion=self.is_duplicate_deletion_skipped(attribute_type=tracking_category["Name"].upper().replace(" ", "_"), is_tracking_category=True),
                app_name=get_app_name(),
                attribute_disable_callback_path=self.get_attribute_disable_callback_path(attribute_type=tracking_category["Name"].upper().replace(" ", "_")),
                is_import_to_fyle_enabled=self.is_import_enabled(attribute_type=tracking_category["Name"].upper().replace(" ", "_"), is_tracking_category=True)
            )

        return []

    def sync_items(self):
        """
        Get Items
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)

        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        updated_at = get_last_synced_at(self.workspace_id, "ITEM")

        items = self.connection.items.get_all(modified_after=updated_at)["Items"]

        item_attributes = []

        for item in items:
            item_attributes.append(
                {
                    "attribute_type": "ITEM",
                    "display_name": "Item",
                    "value": item["Code"],
                    "destination_id": item["ItemID"],
                    "active": True
                }
            )
        DestinationAttribute.bulk_create_or_update_destination_attributes(
            item_attributes, "ITEM", self.workspace_id, True,
            skip_deletion=self.is_duplicate_deletion_skipped(attribute_type='ITEM'),
            app_name=get_app_name(),
            attribute_disable_callback_path=self.get_attribute_disable_callback_path(attribute_type="ITEM"),
            is_import_to_fyle_enabled=self.is_import_enabled(attribute_type="ITEM")
        )

        return []

    def create_contact_destination_attribute(self, contact):
        created_contact = DestinationAttribute.create_or_update_destination_attribute(
            {
                "attribute_type": "CONTACT",
                "display_name": "Contact",
                "value": contact["Name"],
                "destination_id": contact["ContactID"],
                "detail": {
                    "email": contact["EmailAddress"]
                    if "EmailAddress" in contact
                    else None
                },
                "active": True
            },
            self.workspace_id,
        )

        return created_contact

    def sync_dimensions(self, workspace_id: str):
        try:
            self.sync_accounts()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_contacts()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_customers()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_items()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_tracking_categories()
        except Exception as exception:
            logger.info(exception)

        try:
            self.sync_tax_codes()
        except Exception as exception:
            logger.info(exception)

    def post_contact(self, contact_name: str, email: str):
        """
        Post contact to Xero
        :param contact_name: name of the contact to be created
        :param email: email of the contact
        :return: Contact Destination Attribute
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        contact = {
            "Name": contact_name,
            "FirstName": contact_name.split(" ")[0],
            "LastName": contact_name.split(" ")[-1]
            if len(contact_name.split(" ")) > 1
            else "",
            "EmailAddress": email,
        }

        created_contact = self.connection.contacts.post(contact)["Contacts"][0]

        return created_contact

    def __construct_bill_lineitems(
        self,
        bill_lineitems: List[BillLineItem],
        general_mappings: GeneralMapping,
        general_settings: WorkspaceGeneralSettings,
    ) -> List[Dict]:
        """
        Create bill line items
        :return: constructed line items
        """
        lines = []

        for line in bill_lineitems:
            unit_amount = line.amount
            if line.tax_code:
                unit_amount = line.amount - line.tax_amount
            elif general_mappings:
                unit_amount = self.get_tax_inclusive_amount(
                    line.amount, general_mappings.default_tax_code_id
                )

            tax_type = None
            if line.tax_code and line.tax_amount:
                tax_type = line.tax_code
            elif general_settings.import_tax_codes and general_mappings != None:
                tax_type = general_mappings.default_tax_code_id

            tax_amount = 0.00
            if line.tax_code and line.tax_amount is not None:
                tax_amount = line.tax_amount
            elif general_mappings:
                tax_amount = round(
                    line.amount
                    - self.get_tax_inclusive_amount(
                        line.amount, general_mappings.default_tax_code_id
                    ),
                    2,
                )

            line = {
                "Description": line.description,
                "Quantity": "1",
                "UnitAmount": unit_amount,
                "AccountCode": line.account_id,
                "ItemCode": line.item_code if line.item_code else None,
                "Tracking": line.tracking_categories
                if line.tracking_categories
                else None,
                "TaxType": tax_type,
                "TaxAmount": tax_amount,
            }
            lines.append(line)

        return lines

    def __construct_bill(self, bill: Bill, bill_lineitems: List[BillLineItem]) -> Dict:
        """
        Create a bill
        :return: constructed bill
        """
        general_mappings = GeneralMapping.objects.filter(
            workspace_id=self.workspace_id
        ).first()
        general_settings = WorkspaceGeneralSettings.objects.get(
            workspace_id=self.workspace_id
        )
        workspace = bill.expense_group.workspace

        bill_payload = {
            "Type": "ACCPAY",
            "Contact": {"ContactID": bill.contact_id},
            "Url": f'{settings.FYLE_APP_URL}/app/admin/#/view_expense/{bill_lineitems[0].expense.expense_id}?org_id={workspace.fyle_org_id}' if settings.BRAND_ID == 'fyle' else None,
            "LineAmountTypes": "Exclusive"
            if general_settings.import_tax_codes
            else "NoTax",
            "Reference": bill.reference,
            "InvoiceNumber": bill.reference,
            "Date": bill.date,
            "DueDate": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "CurrencyCode": bill.currency,
            "Status": "AUTHORISED",
            "LineItems": self.__construct_bill_lineitems(
                bill_lineitems, general_mappings, general_settings
            ),
        }

        logger.info("| Payload for Bill creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} BILL_PAYLOAD: {}}}".format(self.workspace_id, bill.expense_group.id, bill_payload))
        return bill_payload

    def post_bill(
        self,
        bill: Bill,
        bill_lineitems: List[BillLineItem],
        general_settings: WorkspaceGeneralSettings,
    ):
        """
        Post vendor bills to Xero
        """

        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        try:
            bills_payload = self.__construct_bill(bill, bill_lineitems)
            created_bill = self.connection.invoices.post(bills_payload)
            return created_bill

        except WrongParamsError as exception:
            detail = json.dumps(exception.__dict__)
            detail = json.loads(detail)

            if detail["message"]["Elements"]:
                if (
                    general_settings.change_accounting_period
                    and "The document date cannot be before the end of year lock date"
                    in detail["message"]["Elements"][0]["ValidationErrors"][0][
                        "Message"
                    ]
                ):
                    first_day_of_month = (
                        datetime.today().date().replace(day=1).strftime("%Y-%m-%d")
                    )
                    bills_payload = self.__construct_bill(bill, bill_lineitems)
                    bills_payload["Date"] = first_day_of_month
                    created_bill = self.connection.invoices.post(bills_payload)
                    return created_bill
                else:
                    raise

    def __construct_bank_transaction_lineitems(
        self,
        bank_transaction_lineitems: List[BankTransactionLineItem],
        general_mappings: GeneralMapping,
        general_settings: WorkspaceGeneralSettings,
    ) -> List[Dict]:
        """
        Create bank transaction line items
        :return: constructed line items
        """
        lines = []

        for line in bank_transaction_lineitems:
            unit_amount = line.amount
            if line.tax_code:
                unit_amount = line.amount - line.tax_amount
            elif general_mappings:
                unit_amount = self.get_tax_inclusive_amount(
                    line.amount, general_mappings.default_tax_code_id
                )

            tax_type = None
            if line.tax_code and line.tax_amount is not None:
                tax_type = line.tax_code
            elif general_settings.import_tax_codes and general_mappings != None:
                tax_type = general_mappings.default_tax_code_id

            line = {
                "Description": line.description,
                "Quantity": "1",
                "UnitAmount": abs(unit_amount),
                "AccountCode": line.account_id,
                "ItemCode": line.item_code if line.item_code else None,
                "Tracking": line.tracking_categories
                if line.tracking_categories
                else None,
                "TaxType": tax_type,
            }
            lines.append(line)

        return lines

    def __construct_bank_transaction(
        self,
        bank_transaction: BankTransaction,
        bank_transaction_lineitems: List[BankTransactionLineItem],
    ) -> Dict:
        """
        Create a bank transaction
        :return: constructed bank transaction
        """
        general_mappings = GeneralMapping.objects.filter(
            workspace_id=self.workspace_id
        ).first()
        general_settings = WorkspaceGeneralSettings.objects.get(
            workspace_id=self.workspace_id
        )
        workspace = bank_transaction.expense_group.workspace

        bank_transaction_payload = {
            "Type": "SPEND",
            "Contact": {"ContactID": bank_transaction.contact_id},
            "BankAccount": {"AccountID": bank_transaction.bank_account_code},
            "Url": f'{settings.FYLE_APP_URL}/app/admin/#/view_expense/{bank_transaction_lineitems[0].expense.expense_id}?org_id={workspace.fyle_org_id}' if settings.BRAND_ID == 'fyle' else None,
            "LineAmountTypes": "Exclusive"
            if general_settings.import_tax_codes
            else "NoTax",
            "Reference": bank_transaction.reference,
            "Date": bank_transaction.transaction_date,
            "CurrencyCode": bank_transaction.currency,
            "Status": "AUTHORISED",
            "LineItems": self.__construct_bank_transaction_lineitems(
                bank_transaction_lineitems, general_mappings, general_settings
            ),
        }

        if bank_transaction_lineitems[0].amount < 0:
            bank_transaction_payload["Type"] = "RECEIVE"

        logger.info("| Payload for Bank Transaction creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} BANK_TRANSACTION_PAYLOAD: {}}}".format(self.workspace_id, bank_transaction.expense_group.id, bank_transaction_payload))
        return bank_transaction_payload

    def post_bank_transaction(
        self,
        bank_transaction: BankTransaction,
        bank_transaction_lineitems: List[BankTransactionLineItem],
        general_settings: WorkspaceGeneralSettings,
    ):
        """
        Post bank transactions to Xero
        """

        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        try:
            bank_transaction_payload = self.__construct_bank_transaction(
                bank_transaction, bank_transaction_lineitems
            )
            created_bank_transaction = self.connection.bank_transactions.post(
                bank_transaction_payload
            )
            return created_bank_transaction

        except WrongParamsError as exception:
            detail = json.dumps(exception.__dict__)
            detail = json.loads(detail)

            if detail["message"]["Elements"]:
                if (
                    general_settings.change_accounting_period
                    and "The document date cannot be before the end of year lock date"
                    in detail["message"]["Elements"][0]["ValidationErrors"][0][
                        "Message"
                    ]
                ):
                    first_day_of_month = (
                        datetime.today().date().replace(day=1).strftime("%Y-%m-%d")
                    )
                    bank_transaction_payload = self.__construct_bank_transaction(
                        bank_transaction, bank_transaction_lineitems
                    )
                    bank_transaction_payload["Date"] = first_day_of_month
                    bank_transaction_payload = self.connection.bank_transactions.post(
                        bank_transaction_payload
                    )
                    return bank_transaction_payload
                else:
                    raise

    def post_attachments(
        self, ref_id: str, ref_type: str, attachments: List[Dict]
    ) -> List:
        """
        Link attachments to objects Xero
        :param ref_id: object id
        :param ref_type: type of object
        :param attachments: attachment[dict()]
        """

        if len(attachments):
            responses = []
            for attachment in attachments:
                response = self.connection.attachments.post_attachment(
                    endpoint=ref_type,
                    filename="{0}_{1}".format(attachment["id"], attachment["name"]),
                    data=base64.b64decode(attachment["download_url"]),
                    guid=ref_id,
                )

                responses.append(response)
            return responses
        return []

    @staticmethod
    def __construct_bill_payment(payment: Payment) -> Dict:
        """
        Create a bill payment
        :param payment: bill_payment object extracted from database
        :return: constructed bill payment
        """
        payment_payload = {
            "Payments": [
                {
                    "Invoice": {"InvoiceId": payment.invoice_id},
                    "Account": {"AccountId": payment.account_id},
                    "Amount": payment.amount,
                }
            ]
        }

        logger.info("| Payload for Bill Payment creation | Content: {{WORKSPACE_ID: {} EXPENSE_GROUP_ID: {} PAYMENT_PAYLOAD: {}}}".format(payment.workspace_id, payment.expense_group.id, payment_payload))
        return payment_payload

    def post_payment(self, payment: Payment):
        """
        Post payment to Xero
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        payment_payload = self.__construct_bill_payment(payment)
        created_payment = self.connection.payments.post(payment_payload)
        return created_payment

    def get_bill(self, bill_id: str):
        """
        Get Bill by id from Xero
        :param bill_id:
        :return:
        """
        tenant_mapping = TenantMapping.objects.get(workspace_id=self.workspace_id)
        self.connection.set_tenant_id(tenant_mapping.tenant_id)

        bill = self.connection.invoices.get_by_id(invoice_id=bill_id)
        return bill
