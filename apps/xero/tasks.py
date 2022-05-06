import json
import logging
import traceback
from datetime import datetime, timedelta
from time import sleep
from typing import List
import base64
import requests

from django.db import transaction
from django.db.models import Q
from django_q.models import Schedule
from django_q.tasks import Chain

from fyle_accounting_mappings.models import Mapping, ExpenseAttribute, DestinationAttribute
from fyle_integrations_platform_connector import PlatformConnector

from xerosdk.exceptions import XeroSDKError, WrongParamsError, InvalidGrant, RateLimitError

from apps.fyle.models import ExpenseGroup, Reimbursement, Expense
from apps.mappings.models import GeneralMapping, TenantMapping
from apps.tasks.models import TaskLog
from apps.workspaces.models import WorkspaceGeneralSettings, XeroCredentials, FyleCredential, Workspace
from apps.xero.models import Bill, BillLineItem, BankTransaction, BankTransactionLineItem, Payment
from apps.xero.utils import XeroConnector
from fyle_xero_api.exceptions import BulkError

logger = logging.getLogger(__name__)
logger.level = logging.INFO

def get_or_create_credit_card_contact(workspace_id: int, merchant: str):
    """
    Get or create credit card contact
    :param workspace_id: Workspace Id
    :param merchant: Fyle Expense Merchant
    :return: Contact
    """

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


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content).decode('ascii')


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
        file_ids = expense_group.expenses.values_list('file_ids', flat=True)
        platform = PlatformConnector(fyle_credentials)

        files_list = []
        attachments = []
        for file_id in file_ids:
            if file_id:
                file_object = {'id': file_id[0]}
                files_list.append(file_object)

        if len(files_list):
            payload = {
                "data": files_list
            }

            attachments = platform.connection.v1beta.admin.files.bulk_generate_file_urls(payload=payload)['data']

            if attachments:
                for attachment in attachments:
                    attachment['download_url'] = get_as_base64(attachment['download_url'])

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
            logger.info('Error while auto creating contact workspace_id - %s error: %s',
                expense_group.workspace_id, {'error': exception.message})

def create_bill(expense_group_id: int, task_log_id: int, xero_connection: XeroConnector):
    sleep(2)
    expense_group = ExpenseGroup.objects.get(id=expense_group_id)
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
    try:
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
        logger.info(
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
        logger.info(exception.response)
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
        task_log.detail = None
        task_log.xero_errors = {
            'error': exception.message
        }

        task_log.save()

    except RateLimitError as exception:
        logger.error(exception.message)
        task_log.status = 'FAILED'
        task_log.detail = None
        task_log.xero_errors = [
            {
                'error': {
                    'Elements': [
                        {
                            'ValidationErrors': [
                                {
                                    'Message': 'Rate limit exceeded, integration will retry exports in a while'
                                }
                            ]
                        }
                    ]
                }
            }
        ]

        task_log.save()

    except XeroSDKError as exception:
        logger.exception(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = None
        task_log.xero_errors = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = None
        task_log.xero_errors = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def create_chain_and_export(chaining_attributes: list, workspace_id: int) -> None:
    """
    Create a chain of expense groups and export them to Xero
    :param chaining_attributes:
    :param workspace_id:
    :return: None
    """
    xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id)
    chain = Chain()
    for group in chaining_attributes:
        trigger_function = 'apps.xero.tasks.create_{}'.format(group['export_type'])
        chain.append(trigger_function, group['expense_group_id'], group['task_log_id'], xero_connection)

    if chain.length():
        chain.run()


def schedule_bills_creation(workspace_id: int, expense_group_ids: List[str]) -> list:
    """
    Schedule bills creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: List of chaining attributes
    """
    chaining_attributes = []
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, bill__id__isnull=True, exported_at__isnull=True
        ).all()

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

            chaining_attributes.append({
                'expense_group_id': expense_group.id,
                'task_log_id': task_log.id,
                'export_type': 'bill'
            })

            task_log.save()

    return chaining_attributes


def create_bank_transaction(expense_group_id: int, task_log_id: int, xero_connection: XeroConnector):
    sleep(2)
    expense_group = ExpenseGroup.objects.get(id=expense_group_id)
    task_log = TaskLog.objects.get(id=task_log_id)
    if task_log.status not in ['IN_PROGRESS', 'COMPLETE']:
        task_log.status = 'IN_PROGRESS'
        task_log.save()
    else:
        return

    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=expense_group.workspace_id)
    try:
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
        logger.info(
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
        logger.info(exception.response)
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
        task_log.detail = None
        task_log.xero_errors = {
            'error': exception.message
        }

        task_log.save()

    except RateLimitError as exception:
        logger.error(exception.message)
        task_log.status = 'FAILED'
        task_log.detail = None
        task_log.xero_errors = [
            {
                'error': {
                    'Elements': [
                        {
                            'ValidationErrors': [
                                {
                                    'Message': 'Rate limit exceeded, integration will retry exports in a while'
                                }
                            ]
                        }
                    ]
                }
            }
        ]

        task_log.save()

    except XeroSDKError as exception:
        logger.exception(exception.response)
        detail = json.loads(exception.response)
        task_log.status = 'FAILED'
        task_log.detail = None
        task_log.xero_errors = detail

        task_log.save()

    except Exception:
        error = traceback.format_exc()
        task_log.detail = None
        task_log.xero_errors = {
            'error': error
        }
        task_log.status = 'FATAL'
        task_log.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', task_log.workspace_id, task_log.detail)


def schedule_bank_transaction_creation(workspace_id: int, expense_group_ids: List[str]) -> list:
    """
    Schedule bank transaction creation
    :param expense_group_ids: List of expense group ids
    :param workspace_id: workspace id
    :return: List of chaining attributes
    """
    chaining_attributes = []
    if expense_group_ids:
        expense_groups = ExpenseGroup.objects.filter(
            Q(tasklog__id__isnull=True) | ~Q(tasklog__status__in=['IN_PROGRESS', 'COMPLETE']),
            workspace_id=workspace_id, id__in=expense_group_ids, banktransaction__id__isnull=True, exported_at__isnull=True
        ).all()

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

            chaining_attributes.append({
                'expense_group_id': expense_group.id,
                'task_log_id': task_log.id,
                'export_type': 'bank_transaction'
            })

            task_log.save()

    return chaining_attributes


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

    if general_settings.import_tax_codes and not (general_mapping.default_tax_code_id or general_mapping.default_tax_code_name): 
        bulk_errors.append({
            'row': None,
            'expense_group_id': expense_group.id,
            'value': 'Default Tax Code',
            'type': 'General Mapping',
            'message': 'Default Tax Code not found'
        })

    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = lineitem.category if (lineitem.category == lineitem.sub_category or lineitem.sub_category == None) else '{0} / {1}'.format(
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

    platform = PlatformConnector(fyle_credentials)
    platform.reimbursements.sync()

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
                logger.info(
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
                logger.info(exception.response)
                detail = exception.response
                task_log.status = 'FAILED'
                task_log.detail = detail

                task_log.save()

            except WrongParamsError as exception:
                logger.info(exception.message)
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
        logger.info(
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

    platform = PlatformConnector(fyle_credentials)
    platform.reimbursements.sync()

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
        reimbursements_list = []
        for reimbursement_id in reimbursement_ids:
            reimbursement_object = {'id': reimbursement_id}
            reimbursements_list.append(reimbursement_object)

        payload = {
            "data": reimbursements_list
        }
        platform.connection.v1beta.admin.reimbursements.bulk_post_reimbursements(payload)
        platform.reimbursements.sync()


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


def create_missing_currency(workspace_id: int):
    """
    Create missing currency in Xero
    :param workspace_id:
    :return:
    """
    try:
        xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
        xero_connection = XeroConnector(xero_credentials, workspace_id)
        tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
        xero_connection.connection.set_tenant_id(tenant_mapping.tenant_id)

        currencies = xero_connection.connection.currencies.get_all()['Currencies']

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)
        my_profile = platform.connection.v1beta.spender.my_profile.get()
        fyle_currency = my_profile['data']['org']['currency']

        existing_currency = list(filter(lambda currency: currency['Code'] == fyle_currency, currencies))

        if not existing_currency:
            xero_connection.connection.currencies.post(data={
             'Code': fyle_currency,
             'Description': fyle_currency
            })
            logger.info('Created missing currency %s in Xero', fyle_currency)

    except Exception as exception:
        logger.exception('Error creating currency in Xero', exception)


def update_xero_short_code(workspace_id: int):
    """
    Update Xero short code
    :param workspace_id:
    :return:
    """
    try:
        xero_credentials = XeroCredentials.objects.get(workspace_id=workspace_id)
        xero_connection = XeroConnector(xero_credentials, workspace_id)

        tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
        xero_connection.connection.set_tenant_id(tenant_mapping.tenant_id)
        short_code = xero_connection.connection.organisations.get_all()[0]['ShortCode']

        workspace = Workspace.objects.get(pk=workspace_id)
        workspace.xero_short_code = short_code
        workspace.save()

        logger.info('Updated Xero short code')

    except Exception as exception:
        logger.exception('Error updating Xero short code', exception)
