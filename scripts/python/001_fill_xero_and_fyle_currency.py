from apps.workspaces.models import Workspace
from apps.fyle.models import Expense
from apps.xero.utils import XeroConnector
from apps.workspaces.models import XeroCredentials, FyleCredential
from fyle_integrations_platform_connector import PlatformConnector
from django.db.models import Q
from time import sleep

workspaces = Workspace.objects.filter(Q(fyle_currency=None) | Q(xero_currency=None)).all()

for workspace in workspaces:
    expense = Expense.objects.filter(org_id=workspace.fyle_org_id).first()
    if workspace.fyle_currency == None and expense:
        workspace.fyle_currency = expense.currency
    elif workspace.fyle_currency == None:
        try:
            fyle_credentials = FyleCredential.objects.get(workspace_id=workspace.id)
            if fyle_credentials:
                sleep(1)
                platform = PlatformConnector(fyle_credentials)
                my_profile = platform.connection.v1beta.spender.my_profile.get()
                fyle_currency = my_profile['data']['org']['currency']
                workspace.fyle_currency = fyle_currency
                print('Updated', workspace.id)
        except Exception as e:
            print("Some error occured")
    if workspace.xero_currency == None:
        try:
            xero_credentials = XeroCredentials.objects.filter(workspace_id=workspace.id).first()
            if xero_credentials:
                sleep(1)
                xero_connector = XeroConnector(xero_credentials, workspace_id=workspace.id)
                company_info = xero_connector.get_organisations()[0]
                workspace.xero_currency = company_info['BaseCurrency']
                print('Updated', xero_credentials.workspace_id)
        except Exception as e:
            print("Some error occured")
    workspace.save()
