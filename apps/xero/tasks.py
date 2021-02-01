import json
import logging
import traceback
from datetime import datetime
from typing import List

from django.db import transaction
from django_q.models import Schedule
from django_q.tasks import Chain
from fyle_accounting_mappings.models import Mapping

from xerosdk.exceptions import XeroSDKError, WrongParamsError

from apps.fyle.models import ExpenseGroup, Reimbursement
from apps.fyle.utils import FyleConnector
from apps.mappings.models import GeneralMapping
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings, XeroCredentials, FyleCredential
from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem, Payment
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
        xero_credentials = XeroCredentials.objects.get(workspace_id=expense_group.workspace_id)

        xero_connection = XeroConnector(xero_credentials, expense_group.workspace_id)

        with transaction.atomic():
            __validate_expense_group(expense_group)

            bill_object = Bill.create_bill(expense_group)

            bill_lineitems_objects = BillLineItem.create_bill_lineitems(expense_group)

            created_bill = xero_connection.post_bill(bill_object, bill_lineitems_objects)

            load_attachments(xero_connection, created_bill['Invoices'][0]['InvoiceID'], 'invoices', expense_group)

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
            'message': 'Xero Account not connected'
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

    except WrongParamsError as exception:
        all_details = []
        logger.exception(exception)
        detail = json.dumps(exception.__dict__)
        detail = json.loads(detail)

        all_details.append({
            'expense_group_id': expense_group.id,
            'message': detail['message']['Message'],
            'error': detail['message']
        })
        task_log.xero_errors = all_details
        task_log.detail = None
        task_log.status = 'FAILED'

        task_log.save(update_fields=['detail', 'status', 'xero_errors'])

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


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, id__in=expense_group_ids, bill__id__isnull=True
        ).all()
    else:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, bill__id__isnull=True
        ).all()

    chain = Chain(cached=True)

    for expense_group in expense_groups:
        task_log, _ = TaskLog.objects.update_or_create(
            workspace_id=expense_group.workspace_id,
            expense_group=expense_group,
            defaults={
                'status': 'IN_PROGRESS',
                'type': 'CREATING_BILL'
            }
        )

        chain.append('apps.xero.tasks.create_bill', expense_group, task_log)

        task_log.save()

    if chain.length():
        chain.run()


def create_bank_transaction(expense_group, task_log):
    try:
        xero_credentials = XeroCredentials.objects.get(workspace_id=expense_group.workspace_id)

        xero_connection = XeroConnector(xero_credentials, expense_group.workspace_id)

        with transaction.atomic():
            __validate_expense_group(expense_group)

            bank_transaction_object = BankTransaction.create_bank_transaction(expense_group)

            bank_transaction_lineitems_objects = BankTransactionLineItem.create_bank_transaction_lineitems(
                expense_group
            )

            created_bank_transaction = xero_connection.post_bank_transaction(
                bank_transaction_object, bank_transaction_lineitems_objects
            )

            load_attachments(xero_connection, created_bank_transaction['BankTransactions'][0]['BankTransactionID'],
                             'banktransactions', expense_group)

            task_log.detail = created_bank_transaction
            task_log.bank_transaction = bank_transaction_object
            task_log.status = 'COMPLETE'

            task_log.save(update_fields=['detail', 'bank_transaction', 'status'])

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
            'message': 'Xero Account not connected'
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

    except WrongParamsError as exception:
        all_details = []
        logger.exception(exception)
        detail = json.dumps(exception.__dict__)
        detail = json.loads(detail)

        all_details.append({
            'expense_group_id': expense_group.id,
            'message': detail['message']['Message'],
            'error': detail['message']
        })
        task_log.xero_errors = all_details
        task_log.detail = None
        task_log.status = 'FAILED'

        task_log.save(update_fields=['detail', 'status', 'xero_errors'])

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


def schedule_bank_transaction_creation(workspace_id: int, expense_group_ids: List[str]):
    """
    Schedule bank transaction creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: None
    """
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, id__in=expense_group_ids, banktransaction__id__isnull=True
        ).all()
    else:
        expense_groups = ExpenseGroup.objects.filter(
            workspace_id=workspace_id, banktransaction__id__isnull=True
        ).all()

    chain = Chain(cached=True)

    for expense_group in expense_groups:
        task_log, _ = TaskLog.objects.update_or_create(
            workspace_id=expense_group.workspace_id,
            expense_group=expense_group,
            defaults={
                'status': 'IN_PROGRESS',
                'type': 'CREATING_BANK_TRANSACTION'
            }
        )

        chain.append('apps.xero.tasks.create_bank_transaction', expense_group, task_log)

        task_log.save()

    if chain.length():
        chain.run()


def __validate_expense_group(expense_group: ExpenseGroup):
    bulk_errors = []
    row = 0

    general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(
        workspace_id=expense_group.workspace_id)

    if general_settings.corporate_credit_card_expenses_object:
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


def check_expenses_reimbursement_status(expenses):
    all_expenses_paid = True

    for expense in expenses:
        reimbursement = Reimbursement.objects.filter(settlement_id=expense.settlement_id).first()

        if reimbursement.state != 'COMPLETE':
            all_expenses_paid = False

    return all_expenses_paid


def create_payment(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    fyle_connector = FyleConnector(fyle_credentials.refresh_token, workspace_id)

    fyle_connector.sync_reimbursements()

    bills: List[Bill] = Bill.objects.filter(
        payment_synced=False, expense_group__workspace_id=workspace_id,
        expense_group__fund_source='PERSONAL').all()

    general_mappings: GeneralMapping = GeneralMapping.objects.get(workspace_id=workspace_id)

    for bill in bills:
        expense_group_reimbursement_status = check_expenses_reimbursement_status(bill.expense_group.expenses.all())

        if expense_group_reimbursement_status:
            task_log, _ = TaskLog.objects.update_or_create(
                workspace_id=workspace_id,
                task_id='PAYMENT_{}'.format(bill.expense_group.id),
                defaults={
                    'status': 'IN_PROGRESS',
                    'type': 'CREATING_PAYMENT'
                }
            )
            try:
                with transaction.atomic():
                    xero_object_task_log = TaskLog.objects.get(expense_group=bill.expense_group)

                    invoice_id = xero_object_task_log.detail['Id']

                    payment_object = Payment.create_payment(
                        expense_group=bill.expense_group,
                        invoice_id=invoice_id,
                        account_id=general_mappings.payment_account_id
                    )

                    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)

                    xero_connection = XeroConnector(xero_credentials, workspace_id)

                    created_payment = xero_connection.post_payment(
                        payment_object
                    )

                    bill.payment_synced = True
                    bill.paid_on_xero = True
                    bill.save(update_fields=['payment_synced', 'paid_on_xero'])

                    task_log.detail = created_payment
                    task_log.payment = payment_object
                    task_log.status = 'COMPLETE'

                    task_log.save(update_fields=['detail', 'payment', 'status'])

            except XeroCredentials.DoesNotExist:
                logger.error(
                    'Xero Credentials not found for workspace_id %s / expense group %s',
                    workspace_id,
                    bill.expense_group
                )
                detail = {
                    'expense_group_id': bill.expense_group,
                    'message': 'Xero Account not connected'
                }
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save(update_fields=['detail', 'status'])

            except BulkError as exception:
                logger.error(exception.response)
                detail = exception.response
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save(update_fields=['detail', 'status'])

            except WrongParamsError as exception:
                logger.error(exception.response)
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
                logger.error('Something unexpected happened workspace_id: %s %s',
                             task_log.workspace_id, task_log.detail)


def schedule_payment_creation(sync_fyle_to_xero_payments, workspace_id):
    general_mappings: GeneralMapping = GeneralMapping.objects.filter(workspace_id=workspace_id).first()
    if general_mappings:
        if sync_fyle_to_xero_payments and general_mappings.payment_account_id:
            start_datetime = datetime.now()
            schedule, _ = Schedule.objects.update_or_create(
                func='apps.xero.tasks.create_payment',
                args='{}'.format(workspace_id),
                defaults={
                    'schedule_type': Schedule.MINUTES,
                    'minutes': 24 * 60,
                    'next_run': start_datetime
                }
            )
    if not sync_fyle_to_xero_payments:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.xero.tasks.create_payment',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()
