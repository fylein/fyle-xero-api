import logging
import os

from fyle.platform import Platform
from fyle.platform.exceptions import InvalidTokenError

from apps.workspaces.models import FyleCredential
from .apis import Expenses, Employees, Categories, Projects, CostCenters, ExpenseCustomFields, CorporateCards, \
    Reimbursements, TaxGroups, Merchants, Files, DependentFields, Departments, Subscriptions

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class PlatformConnector:
    """The main class creates a connection with Fyle Platform APIs using OAuth2 authentication
    (refresh token grant type).

    Parameters:
    fyle_credential (str): Fyle Credential instance.
    """

    def __init__(self, fyle_credentials: FyleCredential):
        server_url = '{}/platform/v1beta'.format(fyle_credentials.cluster_domain)
        self.workspace_id = fyle_credentials.workspace_id
        try:
            self.connection = Platform(
                server_url=server_url,
                token_url=os.environ.get('FYLE_TOKEN_URI'),
                client_id=os.environ.get('FYLE_CLIENT_ID'),
                client_secret=os.environ.get('FYLE_CLIENT_SECRET'),
                refresh_token=fyle_credentials.refresh_token
            )
            
        except Exception:
            logger.info('Invalid refresh token')
            raise InvalidTokenError('Invalid refresh token')

        self.expenses = Expenses()
        self.employees = Employees()
        self.categories = Categories()
        self.projects = Projects()
        self.cost_centers = CostCenters()
        self.expense_custom_fields = ExpenseCustomFields()
        self.corporate_cards = CorporateCards()
        self.reimbursements = Reimbursements()
        self.tax_groups = TaxGroups()
        self.merchants = Merchants()
        self.files = Files()
        self.departments = Departments()
        self.dependent_fields = DependentFields()
        self.subscriptions = Subscriptions()

        self.set_connection()
        self.set_workspace_id()

    def set_connection(self):
        """Set connection with Fyle Platform APIs."""
        self.expenses.set_connection(self.connection.v1beta.admin.expenses)
        self.employees.set_connection(self.connection.v1beta.admin.employees)
        self.categories.set_connection(self.connection.v1beta.admin.categories)
        self.projects.set_connection(self.connection.v1beta.admin.projects)
        self.cost_centers.set_connection(self.connection.v1beta.admin.cost_centers)
        self.expense_custom_fields.set_connection(self.connection.v1beta.admin.expense_fields)
        self.corporate_cards.set_connection(self.connection.v1beta.admin.corporate_cards)
        self.reimbursements.set_connection(self.connection.v1beta.admin.reimbursements)
        self.tax_groups.set_connection(self.connection.v1beta.admin.tax_groups)
        self.merchants.set_connection(self.connection.v1beta.admin.expense_fields)
        self.files.set_connection(self.connection.v1beta.admin.files)
        self.departments.set_connection(self.connection.v1beta.admin.departments)
        self.dependent_fields.set_connection(
            self.connection.v1beta.admin.dependent_expense_field_values,
            self.connection.v1beta.admin.expense_fields
        )
        self.subscriptions.set_connection(self.connection.v1beta.admin.subscriptions)

    def set_workspace_id(self):
        """Set workspace ID for Fyle Platform APIs."""
        self.expenses.set_workspace_id(self.workspace_id)
        self.employees.set_workspace_id(self.workspace_id)
        self.categories.set_workspace_id(self.workspace_id)
        self.projects.set_workspace_id(self.workspace_id)
        self.cost_centers.set_workspace_id(self.workspace_id)
        self.expense_custom_fields.set_workspace_id(self.workspace_id)
        self.corporate_cards.set_workspace_id(self.workspace_id)
        self.reimbursements.set_workspace_id(self.workspace_id)
        self.tax_groups.set_workspace_id(self.workspace_id)
        self.merchants.set_workspace_id(self.workspace_id)
        self.files.set_workspace_id(self.workspace_id)
        self.departments.set_workspace_id(self.workspace_id)
        self.dependent_fields.set_workspace_id(self.workspace_id)

    def import_fyle_dimensions(self, import_taxes: bool = False, import_dependent_fields: bool = False):
        """Import Fyle Platform dimension."""
        apis = ['employees', 'categories', 'projects', 'cost_centers', 'expense_custom_fields', 'corporate_cards']

        if import_dependent_fields:
            apis.append('dependent_fields')

        if import_taxes:
            apis.append('tax_groups')

        for api in apis:
            dimension = getattr(self, api)
            try:
                dimension.sync()
            except Exception as e:
                logger.exception(e)
