import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import List

from django.db import transaction
from django.db.models import Q
from django_q.models import Schedule
from django_q.tasks import Chain
from fyle_accounting_mappings.models import Mapping, ExpenseAttribute, DestinationAttribute

from xerosdk.exceptions import XeroSDKError, WrongParamsError, InvalidGrant

from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.fyle.utils import FyleConnector
from apps.mappings.models import GeneralMapping
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings, XeroCredentials, FyleCredential
from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem, Payment
from apps.xero.utils import XeroConnector
from fyle_xero_api.exceptions import BulkError

logger = logging.getLogger(__name__)


def get_or_create_credit_card_contact(workspace_id: int, merchant: str):
    """
    Get or create credit card contact
    :param workspace_id: Workspace Id
    :param merchant: Fyle Expense Merchant
    :return: Contact
    """
    try:
        xero_credentials =  XeroCredentials.objects.get(workspace_id=workspace_id)
        xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)
        contact = None

        if merchant:
            try:
                contact = xero_connection.get_or_create_contact(merchant, create=False)
            except WrongParamsError as bad_request:
                logger.error(bad_request.message)

        if not contact:
            contact = xero_connection.get_or_create_contact('Credit Card Misc', create=True)

        return contact

    except XeroCredentials.DoesNotExist:
        logger.error(
            'Xero Credentials not found for workspace_id %s',
            workspace_id,
        )


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


def create_or_update_employee_mapping(expense_group: ExpenseGroup, xero_connection: XeroConnector,
                                      auto_map_employees_preference: str):
    try:
        Mapping.objects.get(
            destination_type='CONTACT',
            source_type='EMPLOYEE',
            source__value=expense_group.description.get('employee_email'),
            workspace_id=expense_group.workspace_id
        )
    
    except Mapping.DoesNotExist:
        source_employee = ExpenseAttribute.objects.get(
            workspace_id=expense_group.workspace_id,
            attribute_type='EMPLOYEE',
            value=expense_group.description.get('employee_email')
        )

        try:
            if auto_map_employees_preference == 'EMAIL':
                filters = {
                    'detail__email__iexact': source_employee.value
                }

            elif auto_map_employees_preference == 'NAME':
                filters = {
                    'value__iexact': source_employee.detail['full_name']
                }

            contact = DestinationAttribute.objects.filter(
                attribute_type='CONTACT',
                workspace_id=expense_group.workspace_id,
                **filters
            ).first()

            if contact is None:
                contact: DestinationAttribute = xero_connection.get_or_create_contact(
                    contact_name=source_employee.detail['full_name'],
                    email=source_employee.value,
                    create=True
                )

            mapping = Mapping.create_or_update_mapping(
                source_type='EMPLOYEE',
                source_value=expense_group.description.get('employee_email'),
                destination_type='CONTACT',
                destination_id=contact.destination_id,
                destination_value=contact.value,
                workspace_id=int(expense_group.workspace_id)
            )

            mapping.source.auto_mapped = True
            mapping.source.save()

            mapping.destination.auto_created = True
            mapping.destination.save()

        except WrongParamsError as exception:
            logger.error('Error while auto creating contact workspace_id - %s error: %s',
                expense_group.workspace_id, {'error': exception.message})

def create_bill(expense_group, task_log_id):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
    try:
        xero_credentials = XeroCredentials.objects.get(workspace_id=expense_group.workspace_id)
        xero_connection = XeroConnector(xero_credentials, expense_group.workspace_id)

        if general_settings.auto_map_employees and general_settings.auto_create_destination_entity \
                and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
            create_or_update_employee_mapping(expense_group, xero_connection, general_settings.auto_map_employees)

        with transaction.atomic():
            __validate_expense_group(expense_group)

            bill_object = Bill.create_bill(expense_group)

            bill_lineitems_objects = BillLineItem.create_bill_lineitems(expense_group)

            created_bill = xero_connection.post_bill(bill_object, bill_lineitems_objects)

            load_attachments(xero_connection, created_bill['Invoices'][0]['InvoiceID'], 'invoices', expense_group)

            task_log.detail = created_bill
            task_log.bill = bill_object
            task_log.xero_errors = None
            task_log.status = 'COMPLETE'

            task_log.save()

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

        task_log.save()

    except BulkError as exception:
        logger.exception(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

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

        task_log.save()

    except InvalidGrant as exception:
        logger.exception(exception.message)
        task_log.status = 'FAILED'
        task_log.detail = {
            'error': exception.message
        }

        task_log.save()

    except XeroSDKError as exception:
        logger.exception(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
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
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, bill__id__isnull=True, exported_at__isnull=True
        ).all()

        chain = Chain()

        for expense_group in expense_groups:
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_BILL'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.status = 'ENQUEUED'
                task_log.save()

            chain.append('apps.xero.tasks.create_bill', expense_group, task_log.id)

            task_log.save()

        if chain.length():
            chain.run()


def create_bank_transaction(expense_group: ExpenseGroup, task_log_id):
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
    try:
        xero_credentials = XeroCredentials.objects.get(workspace_id=expense_group.workspace_id)
        xero_connection = XeroConnector(xero_credentials, expense_group.workspace_id)

        if not general_settings.map_merchant_to_contact:
            if general_settings.auto_map_employees and general_settings.auto_create_destination_entity \
                    and general_settings.auto_map_employees != 'EMPLOYEE_CODE':
                create_or_update_employee_mapping(expense_group, xero_connection, general_settings.auto_map_employees)
        else:
            merchant = expense_group.expenses.first().vendor
            get_or_create_credit_card_contact(expense_group.workspace_id, merchant)

        with transaction.atomic():
            __validate_expense_group(expense_group)

            bank_transaction_object = BankTransaction.create_bank_transaction(expense_group, general_settings.map_merchant_to_contact)

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
            task_log.xero_errors = None
            task_log.status = 'COMPLETE'

            task_log.save()

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

        task_log.save()

    except BulkError as exception:
        logger.exception(exception.response)
        detail = exception.response
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

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

        task_log.save()

    except InvalidGrant as exception:
        logger.exception(exception.message)
        task_log.status = 'FAILED'
        task_log.detail = {
            'error': exception.message
        }

        task_log.save()

    except XeroSDKError as exception:
        logger.exception(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
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
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, banktransaction__id__isnull=True, exported_at__isnull=True
        ).all()

        chain = Chain()

        for expense_group in expense_groups:
            task_log, _ = TaskLog.objects.get_or_create(
                workspace_id=expense_group.workspace_id,
                expense_group=expense_group,
                defaults={
                    'status': 'ENQUEUED',
                    'type': 'CREATING_BANK_TRANSACTION'
                }
            )
            if task_log.status not in ['IN_PROGRESS', 'ENQUEUED']:
                task_log.status = 'ENQUEUED'
                task_log.save()

            chain.append('apps.xero.tasks.create_bank_transaction', expense_group, task_log.id)

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
    
    if not (general_settings.corporate_credit_card_expenses_object == 'BANK TRANSACTION'
            and general_settings.map_merchant_to_contact and expense_group.fund_source == 'CCC'):

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
                xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
                xero_connection = XeroConnector(xero_credentials, workspace_id)
                with transaction.atomic():
                    xero_object_task_log = TaskLog.objects.get(expense_group=bill.expense_group)

                    invoice_id = xero_object_task_log.detail['Invoices'][0]['InvoiceID']

                    payment_object = Payment.create_payment(
                        expense_group=bill.expense_group,
                        invoice_id=invoice_id,
                        account_id=general_mappings.payment_account_id
                    )

                    created_payment = xero_connection.post_payment(
                        payment_object
                    )

                    bill.payment_synced = True
                    bill.paid_on_xero = True
                    bill.save()

                    task_log.detail = created_payment
                    task_log.payment = payment_object
                    task_log.xero_errors = None
                    task_log.status = 'COMPLETE'

                    task_log.save()

            except XeroCredentials.DoesNotExist:
                logger.error(
                    'Xero Credentials not found for workspace_id %s / expense group %s',
                    workspace_id,
                    bill.expense_group.id
                )
                detail = {
                    'expense_group_id': bill.expense_group.id,
                    'message': 'Xero Account not connected'
                }
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save()

            except BulkError as exception:
                logger.error(exception.response)
                detail = exception.response
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save()

            except WrongParamsError as exception:
                logger.error(exception.message)
                detail = exception.message
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save()

            except Exception:
                error = traceback.format_exc()
                task_log.detail = {
                    'error': error
                }
                task_log.status = 'FATAL'
                task_log.save()
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


def get_all_xero_bill_ids(xero_objects):
    xero_objects_details = {}

    expense_group_ids = [xero_object.expense_group_id for xero_object in xero_objects]

    task_logs = TaskLog.objects.filter(expense_group_id__in=expense_group_ids).all()

    for task_log in task_logs:
        xero_objects_details[task_log.expense_group.id] = {
            'expense_group': task_log.expense_group,
            'bill_id': task_log.detail['Invoices'][0]['InvoiceID']
        }

    return xero_objects_details


def check_xero_object_status(workspace_id):
    try:
        xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)

        xero_connection = XeroConnector(xero_credentials, workspace_id)

        bills = Bill.objects.filter(
            expense_group__workspace_id=workspace_id,
            paid_on_xero=False,
            expense_group__fund_source='PERSONAL'
        ).all()

        if bills:
            bill_id_map = get_all_xero_bill_ids(bills)

            for bill in bills:
                bill_object = xero_connection.get_bill(bill_id_map[bill.expense_group.id]['bill_id'])

                if bill_object['Invoices'][0]['Status'] == 'PAID':
                    line_items = BillLineItem.objects.filter(bill_id=bill.id)
                    for line_item in line_items:
                        expense = line_item.expense
                        expense.paid_on_xero = True
                        expense.save()

                    bill.paid_on_xero = True
                    bill.payment_synced = True
                    bill.save()

    except XeroCredentials.DoesNotExist:
        logger.error(
            'Xero Credentials not found for workspace_id %s',
            workspace_id,
        )


def schedule_xero_objects_status_sync(sync_xero_to_fyle_payments, workspace_id):
    if sync_xero_to_fyle_payments:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.xero.tasks.check_xero_object_status',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.xero.tasks.check_xero_object_status',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def process_reimbursements(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    fyle_connector = FyleConnector(fyle_credentials.refresh_token, workspace_id)

    fyle_connector.sync_reimbursements()

    reimbursements = Reimbursement.objects.filter(state='PENDING', workspace_id=workspace_id).all()

    reimbursement_ids = []

    if reimbursements:
        for reimbursement in reimbursements:
            expenses = Expense.objects.filter(settlement_id=reimbursement.settlement_id, fund_source='PERSONAL').all()
            paid_expenses = expenses.filter(paid_on_xero=True)

            all_expense_paid = False
            if len(expenses):
                all_expense_paid = len(expenses) == len(paid_expenses)

            if all_expense_paid:
                reimbursement_ids.append(reimbursement.reimbursement_id)

    if reimbursement_ids:
        fyle_connector.post_reimbursement(reimbursement_ids)
        fyle_connector.sync_reimbursements()


def schedule_reimbursements_sync(sync_xero_to_fyle_payments, workspace_id):
    if sync_xero_to_fyle_payments:
        start_datetime = datetime.now() + timedelta(hours=12)
        schedule, _ = Schedule.objects.update_or_create(
            func='apps.xero.tasks.process_reimbursements',
            args='{}'.format(workspace_id),
            defaults={
                'schedule_type': Schedule.MINUTES,
                'minutes': 24 * 60,
                'next_run': start_datetime
            }
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func='apps.xero.tasks.process_reimbursements',
            args='{}'.format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()