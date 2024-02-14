from datetime import datetime

from django.conf import settings
from django.db.models import Q

from apps.fyle.actions import __bulk_update_expenses
from apps.fyle.helpers import get_updated_accounting_export_summary
from apps.fyle.models import Expense
from apps.tasks.models import TaskLog
from apps.workspaces.models import Workspace

# PLEASE RUN sql/scripts/022-fill-skipped-accounting-export-summary.sql BEFORE RUNNING THIS SCRIPT


export_types = ['CREATING_BILL', 'CREATING_BANK_TRANSACTION']
task_statuses = ['COMPLETE', 'FAILED', 'FATAL']


# We'll handle all COMPLETE, ERROR expenses in this script
workspaces = Workspace.objects.filter(
    ~Q(name__icontains='fyle for') & ~Q(name__icontains='test')
)

start_time = datetime.now()
number_of_expenses_without_accounting_export_summary = Expense.objects.filter(
    accounting_export_summary__state__isnull=True
).count()
print('Number of expenses without accounting export summary - {}'.format(number_of_expenses_without_accounting_export_summary))
for workspace in workspaces:
    task_logs_count = TaskLog.objects.filter(
        type__in=export_types,
        workspace_id=workspace.id,
        status__in=task_statuses
    ).count()
    print('Updating summary from workspace - {} with ID - {}'.format(workspace.name, workspace.id))
    print('Number of task logs to be updated - {}'.format(task_logs_count))
    page_size = 200
    for offset in range(0, task_logs_count, page_size):
        expense_to_be_updated = []
        limit = offset + page_size
        paginated_task_logs = TaskLog.objects.filter(
            type__in=export_types,
            workspace_id=workspace.id,
            status__in=task_statuses
        )[offset:limit]
        for task_log in paginated_task_logs:
            expense_group = task_log.expense_group
            state = 'ERROR' if task_log.status == 'FAILED' or task_log.status == 'FATAL' else 'COMPLETE'
            error_type = None
            url = None
            if task_log.status == 'FAILED' or task_log.status == 'FATAL':
                for item in task_log.detail:
                    if item.get('type') and item.get('type') == 'Category Mapping':
                        error_type = 'MAPPING'
                    else:
                        error_type = 'ACCOUNTING_INTEGRATION_ERROR'
                url = '{}/workspaces/main/dashboard'.format(settings.XERO_INTEGRATION_APP_URL)
            else:
                try:
                    if task_log.type == 'CREATING_BILL':
                        export_id = expense_group.response_logs['Invoices'][0]['InvoiceID']
                        if workspace.xero_short_code:
                            url = f'https://go.xero.com/organisationlogin/default.aspx?shortcode={workspace.xero_short_code}&redirecturl=/AccountsPayable/Edit.aspx?InvoiceID={export_id}'
                        else:
                            url = f'https://go.xero.com/AccountsPayable/View.aspx?invoiceID={export_id}'
                    else:
                        export_id = expense_group.response_logs['BankTransactions'][0]['BankTransactionID']
                        account_id = expense_group.response_logs['BankTransactions'][0]['BankAccount']['AccountID']
                        if workspace.xero_short_code:
                            url = f'https://go.xero.com/organisationlogin/default.aspx?shortcode={workspace.xero_short_code}&redirecturl=/Bank/ViewTransaction.aspx?bankTransactionID={export_id}'
                        else:
                            url = f'https://go.xero.com/Bank/ViewTransaction.aspx?bankTransactionID={export_id}&accountID={account_id}'
                except Exception as error:
                    # Defaulting it to Intacct app url, worst case scenario if we're not able to parse it properly
                    url = 'https://go.xero.com'
                    print('Error while parsing response logs for expense group - {}. Error - {}'.format(expense_group.id, error))
            for expense in expense_group.expenses.filter(accounting_export_summary__state__isnull=True):
                if url:
                    expense_to_be_updated.append(
                        Expense(
                            id=expense.id,
                            accounting_export_summary=get_updated_accounting_export_summary(
                                expense.expense_id,
                                state,
                                error_type,
                                url,
                                False
                            )
                        )
                    )
        print('Updating {} expenses in batches of 50'.format(len(expense_to_be_updated)))
        __bulk_update_expenses(expense_to_be_updated)


number_of_expenses_without_accounting_export_summary = Expense.objects.filter(
    accounting_export_summary__state__isnull=True
).count()
print('Number of expenses without accounting export summary - {}'.format(number_of_expenses_without_accounting_export_summary))
end_time = datetime.now()
print('Time taken - {}'.format(end_time - start_time))
