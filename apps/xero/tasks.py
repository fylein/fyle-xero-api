import json
import logging
import traceback
from datetime import datetime

from django.db import transaction
from fyle_accounting_mappings.models import Mapping

from xerosdk.exceptions import XeroSDKError

from apps.fyle.models import ExpenseGroup
from apps.fyle.utils import FyleConnector
from apps.mappings.models import GeneralMapping
from apps.workspaces.models import WorkspaceGeneralSettings, XeroCredentials, FyleCredential
from apps.xero.models import Bill, BillLineItem
from apps.xero.utils import XeroConnector
from fyle_xero_api.exceptions import BulkError

logger = logging.getLogger(__name__)


def load_attachments(xero_connection: XeroConnector, ref_id: str, ref_type: str, expense_group: ExpenseGroup):
    """
    Get attachments from fyle
    :param xero_connection: Xero Connection
    :param ref_id: object id
    :param ref_type: type of object
    :param expense_group: Expense group
    """
    try:
        fyle_credentials = FyleCredential.objects.get(workspace_id=expense_group.workspace_id)
        expense_ids = expense_group.expenses.values_list('expense_id', flat=True)
        fyle_connector = FyleConnector(fyle_credentials.refresh_token, expense_group.workspace_id)
        attachments = fyle_connector.get_attachments(expense_ids)
        xero_connection.post_attachments(ref_id, ref_type, attachments)
    except Exception:
        error = traceback.format_exc()
        logger.exception(
            'Attachment failed for expense group id %s / workspace id %s \n Error: %s',
            expense_group.id, expense_group.workspace_id, {'error': error}
        )


def create_bill(expense_group, task_log):
    try:
        with transaction.atomic():
            __validate_expense_group(expense_group)

            bill_object = Bill.create_bill(expense_group)

            bill_lineitems_objects = BillLineItem.create_bill_lineitems(expense_group)

            xero_credentials = XeroCredentials.objects.get(workspace_id=expense_group.workspace_id)

            xero_connection = XeroConnector(xero_credentials, expense_group.workspace_id)

            created_bill = xero_connection.post_bill(bill_object, bill_lineitems_objects)

            load_attachments(xero_connection, created_bill['InvoiceId'], 'invoices', expense_group)

            task_log.detail = created_bill
            task_log.bill = bill_object
            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'bill', 'status'])

            expense_group.exported_at = datetime.now()
            expense_group.save()

    except XeroCredentials.DoesNotExist:
        logger.exception(
            'Xero Credentials not found for workspace_id %s / expense group %s',
            expense_group.workspace_id,
            expense_group.id
        )
        detail = {
            'expense_group_id': expense_group.id,
            'message': 'QBO Account not connected'
        }
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except BulkError as exception:
        logger.exception(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except XeroSDKError as exception:
        logger.exception(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save(update_fields=['detail', 'status'])

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save(update_fields=['detail', 'status'])
        logger.exception('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def __validate_expense_group(expense_group: ExpenseGroup):
    bulk_errors = []
    row = 0

    general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(
        workspace_id=expense_group.workspace_id)

    if not general_settings.corporate_credit_card_expenses_object:
        general_mapping = GeneralMapping.objects.filter(workspace_id=expense_group.workspace_id).first()

        if not general_mapping:
            bulk_errors.append({
                'row': None,
                'expense_group_id': expense_group.id,
                'value': 'bank account',
                'type': 'General Mapping',
                'message': 'General mapping not found'
            })

    try:
        Mapping.objects.get(
            destination_type='CONTACT',
            source_type='EMPLOYEE',
            source__value=expense_group.description.get('employee_email'),
            workspace_id=expense_group.workspace_id
        )
    except Mapping.DoesNotExist:
        bulk_errors.append({
            'row': None,
            'expense_group_id': expense_group.id,
            'value': expense_group.description.get('employee_email'),
            'type': 'Employee Mapping',
            'message': 'Employee mapping not found'
        })

    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
            lineitem.category, lineitem.sub_category)

        account = Mapping.objects.filter(
            source_type='CATEGORY',
            source__value=category,
            workspace_id=expense_group.workspace_id
        ).first()
        if not account:
            bulk_errors.append({
                'row': row,
                'expense_group_id': expense_group.id,
                'value': category,
                'type': 'Category Mapping',
                'message': 'Category Mapping not found'
            })

        row = row + 1

    if bulk_errors:
        raise BulkError('Mappings are missing', bulk_errors)
