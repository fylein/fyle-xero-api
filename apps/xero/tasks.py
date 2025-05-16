import logging
import traceback
from datetime import datetime, timezone
from time import sleep
from typing import List

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone as django_timezone
from fyle.platform.exceptions import InternalServerError
from fyle.platform.exceptions import InvalidTokenError as FyleInvalidTokenError
from fyle_accounting_mappings.models import DestinationAttribute, ExpenseAttribute, Mapping
from fyle_integrations_platform_connector import PlatformConnector
from xerosdk.exceptions import UnsuccessfulAuthentication, WrongParamsError

from apps.fyle.actions import post_accounting_export_summary, update_complete_expenses, update_expenses_in_progress
from apps.fyle.enums import FundSourceEnum, FyleAttributeEnum
from apps.fyle.helpers import get_filter_credit_expenses
from apps.fyle.models import Expense, ExpenseGroup, ExpenseGroupSettings
from apps.mappings.models import GeneralMapping, TenantMapping
from apps.tasks.enums import TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import Error, TaskLog
from apps.workspaces.helpers import invalidate_xero_credentials
from apps.workspaces.models import FyleCredential, Workspace, WorkspaceGeneralSettings, XeroCredentials
from apps.xero.exceptions import handle_xero_exceptions, update_last_export_details
from apps.xero.models import BankTransaction, BankTransactionLineItem, Bill, BillLineItem, Payment
from apps.xero.utils import XeroConnector
from fyle_xero_api.exceptions import BulkError
from fyle_xero_api.logging_middleware import get_logger

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def resolve_errors_for_exported_expense_group(expense_group: ExpenseGroup):
    """
    Resolve errors for exported expense group
    :param expense_group: Expense group
    """
    Error.objects.filter(
        workspace_id=expense_group.workspace_id,
        expense_group=expense_group,
        is_resolved=False,
    ).update(is_resolved=True, updated_at=datetime.now(timezone.utc))


def get_or_create_credit_card_contact(
    workspace_id: int, merchant: str, auto_create_merchant_destination_entity
):
    """
    Get or create credit card contact
    :param workspace_id: Workspace Id
    :param merchant: Fyle Expense Merchant
    :return: Contact
    """

    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(
        credentials_object=xero_credentials, workspace_id=workspace_id
    )
    contact = None

    if merchant:
        try:
            contact = xero_connection.get_or_create_contact(merchant, create=False)
        except WrongParamsError as bad_request:
            logger.info(bad_request.message)

        if not contact and auto_create_merchant_destination_entity:
            merchant = merchant
        else:
            merchant = "Credit Card Misc"
    else:
        merchant = "Credit Card Misc"

    try:
        contact = xero_connection.get_or_create_contact(merchant, create=True)
    except WrongParamsError as bad_request:
        logger.error(bad_request.message)

    return contact


def load_attachments(
    xero_connection: XeroConnector,
    ref_id: str,
    ref_type: str,
    expense_group: ExpenseGroup,
):
    """
    Get attachments from fyle
    :param xero_connection: Xero Connection
    :param ref_id: object id
    :param ref_type: type of object
    :param expense_group: Expense group
    """
    try:
        fyle_credentials = FyleCredential.objects.get(
            workspace_id=expense_group.workspace_id
        )
        file_ids = expense_group.expenses.values_list("file_ids", flat=True)
        platform = PlatformConnector(fyle_credentials)

        files_list = []
        attachments = []
        for file_id in file_ids:
            if file_id:
                for id in file_id:
                    file_object = {"id": id}
                    files_list.append(file_object)

        if files_list:
            attachments = platform.files.bulk_generate_file_urls(files_list)

        xero_connection.post_attachments(ref_id, ref_type, attachments)

    except Exception:
        error = traceback.format_exc()
        logger.info(
            "Attachment failed for expense group id %s / workspace id %s \n Error: %s",
            expense_group.id,
            expense_group.workspace_id,
            {"error": error},
        )


def get_employee_expense_attribute(value: str, workspace_id: int) -> ExpenseAttribute:
    """
    Get employee expense attribute
    :param value: value
    :param workspace_id: workspace id
    """
    return ExpenseAttribute.objects.filter(
        attribute_type='EMPLOYEE',
        value=value,
        workspace_id=workspace_id
    ).first()


def sync_inactive_employee(expense_group: ExpenseGroup) -> ExpenseAttribute:
    fyle_credentials = FyleCredential.objects.get(workspace_id=expense_group.workspace_id)
    platform = PlatformConnector(fyle_credentials=fyle_credentials)
    fyle_employee = platform.employees.get_employee_by_email(expense_group.description.get('employee_email'))
    if len(fyle_employee):
        fyle_employee = fyle_employee[0]
        attribute = {
            'attribute_type': 'EMPLOYEE',
            'display_name': 'Employee',
            'value': fyle_employee['user']['email'],
            'source_id': fyle_employee['id'],
            'active': True if fyle_employee['is_enabled'] and fyle_employee['has_accepted_invite'] else False,
            'detail': {
                'user_id': fyle_employee['user_id'],
                'employee_code': fyle_employee['code'],
                'full_name': fyle_employee['user']['full_name'],
                'location': fyle_employee['location'],
                'department': fyle_employee['department']['name'] if fyle_employee['department'] else None,
                'department_id': fyle_employee['department_id'],
                'department_code': fyle_employee['department']['code'] if fyle_employee['department'] else None
            }
        }
        ExpenseAttribute.bulk_create_or_update_expense_attributes([attribute], 'EMPLOYEE', expense_group.workspace_id, True)
        return get_employee_expense_attribute(expense_group.description.get('employee_email'), expense_group.workspace_id)

    return None


def create_or_update_employee_mapping(
    expense_group: ExpenseGroup,
    xero_connection: XeroConnector,
    auto_map_employees_preference: str,
):
    try:
        employee = get_employee_expense_attribute(expense_group.description.get('employee_email'), expense_group.workspace_id)

        if not employee:
            # Sync inactive employee and gracefully handle export failure
            sync_inactive_employee(expense_group)

        Mapping.objects.get(
            destination_type="CONTACT",
            source_type=FyleAttributeEnum.EMPLOYEE,
            source__value=expense_group.description.get("employee_email"),
            workspace_id=expense_group.workspace_id,
        )

    except Mapping.DoesNotExist:
        source_employee = ExpenseAttribute.objects.get(
            workspace_id=expense_group.workspace_id,
            attribute_type=FyleAttributeEnum.EMPLOYEE,
            value=expense_group.description.get("employee_email"),
        )

        try:
            if auto_map_employees_preference == "EMAIL":
                filters = {"detail__email__iexact": source_employee.value}

            elif auto_map_employees_preference == "NAME":
                filters = {"value__iexact": source_employee.detail["full_name"]}

            contact = DestinationAttribute.objects.filter(
                attribute_type="CONTACT",
                workspace_id=expense_group.workspace_id,
                **filters
            ).first()

            if contact is None:
                contact: DestinationAttribute = xero_connection.get_or_create_contact(
                    contact_name=source_employee.detail["full_name"],
                    email=source_employee.value,
                    create=True,
                )

            mapping = Mapping.create_or_update_mapping(
                source_type=FyleAttributeEnum.EMPLOYEE,
                source_value=expense_group.description.get("employee_email"),
                destination_type="CONTACT",
                destination_id=contact.destination_id,
                destination_value=contact.value,
                workspace_id=int(expense_group.workspace_id),
            )

            mapping.source.auto_mapped = True
            mapping.source.save()

            mapping.destination.auto_created = True
            mapping.destination.save()

        except WrongParamsError as exception:
            logger.info(
                "Error while auto creating contact workspace_id - %s error: %s",
                expense_group.workspace_id,
                {"error": exception.message},
            )


def update_expense_and_post_summary(in_progress_expenses: List[Expense], workspace_id: int, fund_source: str) -> None:
    """
    Update expense and post accounting export summary
    :param in_progress_expenses: List of expenses
    :param workspace_id: Workspace ID
    :param fund_source: Fund source
    :return: None
    """
    update_expenses_in_progress(in_progress_expenses)
    post_accounting_export_summary(workspace_id=workspace_id, expense_ids=[expense.id for expense in in_progress_expenses], fund_source=fund_source)


@handle_xero_exceptions(payment=False)
def create_bill(
    expense_group_id: int,
    task_log_id: int,
    xero_connection: XeroConnector,
    last_export: bool,
    is_auto_export: bool,
):
    worker_logger = get_logger()
    sleep(2)
    expense_group = ExpenseGroup.objects.get(id=expense_group_id)
    task_log = TaskLog.objects.get(id=task_log_id)
    worker_logger.info('Creating Bill for Expense Group %s, current state is %s', expense_group.id, task_log.status)

    if task_log.status not in [TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.COMPLETE]:
        task_log.status = TaskLogStatusEnum.IN_PROGRESS
        task_log.save()
    else:
        return

    in_progress_expenses = []
    # Don't include expenses with previous export state as ERROR and it's an auto import/export run
    if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
        try:
            in_progress_expenses.extend(expense_group.expenses.all())
            update_expense_and_post_summary(in_progress_expenses, expense_group.workspace_id, expense_group.fund_source)
        except Exception as e:
            worker_logger.error('Error while updating expenses for expense_group_id: %s and posting accounting export summary %s', expense_group.id, e)

    general_settings = WorkspaceGeneralSettings.objects.get(
        workspace_id=expense_group.workspace_id
    )

    if (
        general_settings.auto_map_employees
        and general_settings.auto_create_destination_entity
        and general_settings.auto_map_employees != "EMPLOYEE_CODE"
    ):
        create_or_update_employee_mapping(
            expense_group, xero_connection, general_settings.auto_map_employees
        )

    __validate_expense_group(expense_group)
    worker_logger.info('Validated Expense Group %s successfully', expense_group.id)

    with transaction.atomic():
        bill_object = Bill.create_bill(expense_group)

        bill_lineitems_objects = BillLineItem.create_bill_lineitems(expense_group, general_settings)

        created_bill = xero_connection.post_bill(
            bill_object, bill_lineitems_objects, general_settings
        )
        worker_logger.info('Created Bill with Expense Group %s successfully', expense_group.id)

        task_log.detail = created_bill
        task_log.bill = bill_object
        task_log.xero_errors = None
        task_log.status = TaskLogStatusEnum.COMPLETE

        task_log.save()

        expense_group.exported_at = datetime.now()
        expense_group.response_logs = created_bill
        expense_group.save()
        resolve_errors_for_exported_expense_group(expense_group)

        if last_export:
            update_last_export_details(expense_group.workspace_id)

        worker_logger.info('Updated Expense Group %s successfully', expense_group.id)

        # Assign billable expenses to customers
        if general_settings.import_customers:
            # Save parent level ID and line item level ID to corresponding exports table to make things easier during posting of linked transaction for debugging purposes
            bill_object.export_id = created_bill["Invoices"][0]["InvoiceID"]
            bill_object.save()

            index = 0
            for bill_lineitems_object in bill_lineitems_objects:
                # Sequence of lines in API response and bank_transaction_lineitems_objects will be the same, iterating over them and adding line item ID
                bill_lineitems_object.line_item_id = created_bill["Invoices"][0][
                    "LineItems"
                ][index]["LineItemID"]
                bill_lineitems_object.save()
                index += 1

            attach_customer_to_export(xero_connection, task_log)

    try:
        generate_export_url_and_update_expense(expense_group, 'BILL')
    except Exception as e:
        worker_logger.error('Error while updating expenses for expense_group_id: %s and posting accounting export summary %s', expense_group.id, e)

    load_attachments(
        xero_connection,
        created_bill["Invoices"][0]["InvoiceID"],
        "invoices",
        expense_group,
    )


def get_linked_transaction_object(export_instance, line_items: list):
    """
    Get linked transaction object
    :param export_instance: export_instance will be either a Bill or a BankTransaction instance
    :param line_items: line_items will be a list of BillLineItem or BankTransactionLineItem instances
    :return: export_id, lines
    """
    lines = []
    export_id = export_instance.export_id

    for line in line_items:
        lines.append(
            {"line_item_id": line.line_item_id, "customer_id": line.customer_id}
        )

    return export_id, lines


def extract_export_lines_contact_ids(task_log: TaskLog):
    """
    Construct linked transaction payload
    :return: export id, lines
    """
    # Constructing orm filter based on export type
    filter = (
        {
            "bill": task_log.bill
        }
        if task_log.type == TaskLogTypeEnum.CREATING_BILL
        else {
            "bank_transaction": task_log.bank_transaction
        }
    )

    # Customer ID is mandatory to create linked transaction
    filter["customer_id__isnull"] = False

    export_id, lines = get_linked_transaction_object(
        export_instance=task_log.bill
        if task_log.type == TaskLogTypeEnum.CREATING_BILL
        else task_log.bank_transaction,
        line_items=BillLineItem.objects.filter(**filter)
        if task_log.type == TaskLogTypeEnum.CREATING_BILL
        else BankTransactionLineItem.objects.filter(**filter),
    )

    return export_id, lines


def attach_customer_to_export(xero_connection: XeroConnector, task_log: TaskLog):
    """
    Attach customer to export
    :param xero_connection:
    :param task_log:
    :return:
    """
    export_id, lines = extract_export_lines_contact_ids(task_log)

    for item in lines:
        try:
            # Linked transaction payload
            data = {
                "SourceTransactionID": export_id,
                "SourceLineItemID": item["line_item_id"],
                "ContactID": item["customer_id"],
            }
            xero_connection.connection.linked_transactions.post(data)

        except Exception as exception:
            # Silently ignoring the error, since the export should be already created
            logger.info(
                "Something unexpected happened during attaching customer to export",
                exception,
            )


@handle_xero_exceptions(payment=False)
def create_bank_transaction(
    expense_group_id: int,
    task_log_id: int,
    xero_connection: XeroConnector,
    last_export: bool,
    is_auto_export: bool,
):
    worker_logger = get_logger()
    sleep(2)
    expense_group = ExpenseGroup.objects.get(id=expense_group_id)
    task_log = TaskLog.objects.get(id=task_log_id)
    worker_logger.info('Creating Bank Transaction for Expense Group %s, current state is %s', expense_group.id, task_log.status)

    if task_log.status not in [TaskLogStatusEnum.IN_PROGRESS, TaskLogStatusEnum.COMPLETE]:
        task_log.status = TaskLogStatusEnum.IN_PROGRESS
        task_log.save()
    else:
        return

    in_progress_expenses = []
    # Don't include expenses with previous export state as ERROR and it's an auto import/export run
    if not (is_auto_export and expense_group.expenses.first().previous_export_state == 'ERROR'):
        try:
            in_progress_expenses.extend(expense_group.expenses.all())
            update_expense_and_post_summary(in_progress_expenses, expense_group.workspace_id, expense_group.fund_source)
        except Exception as e:
            worker_logger.error('Error while updating expenses for expense_group_id: %s and posting accounting export summary %s', expense_group.id, e)

    general_settings = WorkspaceGeneralSettings.objects.get(
        workspace_id=expense_group.workspace_id
    )

    if not general_settings.map_merchant_to_contact:
        if (
            general_settings.auto_map_employees
            and general_settings.auto_create_destination_entity
            and general_settings.auto_map_employees != "EMPLOYEE_CODE"
        ):
            create_or_update_employee_mapping(
                expense_group, xero_connection, general_settings.auto_map_employees
            )
    else:
        merchant = expense_group.expenses.first().vendor
        get_or_create_credit_card_contact(
            expense_group.workspace_id,
            merchant,
            general_settings.auto_create_merchant_destination_entity,
        )

    __validate_expense_group(expense_group)
    worker_logger.info('Validated Expense Group %s successfully', expense_group.id)

    with transaction.atomic():
        bank_transaction_object = BankTransaction.create_bank_transaction(
            expense_group, general_settings.map_merchant_to_contact
        )

        bank_transaction_lineitems_objects = (
            BankTransactionLineItem.create_bank_transaction_lineitems(expense_group, general_settings)
        )

        created_bank_transaction = xero_connection.post_bank_transaction(
            bank_transaction_object,
            bank_transaction_lineitems_objects,
            general_settings,
        )
        worker_logger.info('Created Bank Transaction with Expense Group %s successfully', expense_group.id)

        task_log.detail = created_bank_transaction
        task_log.bank_transaction = bank_transaction_object
        task_log.xero_errors = None
        task_log.status = TaskLogStatusEnum.COMPLETE

        task_log.save()

        expense_group.exported_at = datetime.now()
        expense_group.response_logs = created_bank_transaction
        expense_group.save()
        resolve_errors_for_exported_expense_group(expense_group)

        if last_export:
            update_last_export_details(expense_group.workspace_id)

        worker_logger.info('Updated Expense Group %s successfully', expense_group.id)

        # Assign billable expenses to customers
        if general_settings.import_customers:
            # Save parent level ID and line item level ID to corresponding exports table to make things easier during posting of linked transaction for debugging purposes
            bank_transaction_object.export_id = created_bank_transaction[
                "BankTransactions"
            ][0]["BankTransactionID"]
            bank_transaction_object.save()

            index = 0
            for bank_transaction_lineitems_object in bank_transaction_lineitems_objects:
                # Sequence of lines in API response and bank_transaction_lineitems_objects will be the same, iterating over them and adding line item ID
                bank_transaction_lineitems_object.line_item_id = (
                    created_bank_transaction["BankTransactions"][0]["LineItems"][index][
                        "LineItemID"
                    ]
                )
                bank_transaction_lineitems_object.save()
                index += 1

            attach_customer_to_export(xero_connection, task_log)

    try:
        generate_export_url_and_update_expense(expense_group, 'BANK TRANSACTION')
    except Exception as e:
        worker_logger.error('Error while updating expenses for expense_group_id: %s and posting accounting export summary %s', expense_group.id, e)

    load_attachments(
        xero_connection,
        created_bank_transaction["BankTransactions"][0]["BankTransactionID"],
        "banktransactions",
        expense_group,
    )


def __validate_expense_group(expense_group: ExpenseGroup):
    bulk_errors = []
    row = 0

    general_settings: WorkspaceGeneralSettings = WorkspaceGeneralSettings.objects.get(
        workspace_id=expense_group.workspace_id
    )
    general_mapping = GeneralMapping.objects.filter(
        workspace_id=expense_group.workspace_id
    ).first()

    if general_settings.corporate_credit_card_expenses_object:
        if not general_mapping:
            bulk_errors.append(
                {
                    "row": None,
                    "expense_group_id": expense_group.id,
                    "value": "bank account",
                    "type": "General Mapping",
                    "message": "General mapping not found",
                }
            )

    if not (
        general_settings.corporate_credit_card_expenses_object == "BANK TRANSACTION"
        and general_settings.map_merchant_to_contact
        and expense_group.fund_source == FundSourceEnum.CCC
    ):
        employee_attribute = ExpenseAttribute.objects.filter(
            value=expense_group.description.get("employee_email"),
            workspace_id=expense_group.workspace_id,
            attribute_type=FyleAttributeEnum.EMPLOYEE,
        ).first()

        try:
            Mapping.objects.get(
                destination_type="CONTACT",
                source_type=FyleAttributeEnum.EMPLOYEE,
                source=employee_attribute,
                workspace_id=expense_group.workspace_id,
            )
        except Mapping.DoesNotExist:
            bulk_errors.append(
                {
                    "row": None,
                    "expense_group_id": expense_group.id,
                    "value": expense_group.description.get("employee_email"),
                    "type": "Employee Mapping",
                    "message": "Employee mapping not found",
                }
            )

            if employee_attribute:
                error, created = Error.get_or_create_error_with_expense_group(expense_group, employee_attribute)
                error.increase_repetition_count_by_one(created)

    if general_settings.import_tax_codes:
        if not general_mapping:
            bulk_errors.append(
                {
                    "row": None,
                    "expense_group_id": expense_group.id,
                    "value": "Default Tax Code",
                    "type": "General Mapping",
                    "message": "General mapping not found",
                }
            )
        elif not (
            general_mapping.default_tax_code_id or general_mapping.default_tax_code_name
        ):
            bulk_errors.append(
                {
                    "row": None,
                    "expense_group_id": expense_group.id,
                    "value": "Default Tax Code",
                    "type": "General Mapping",
                    "message": "Default Tax Code not found",
                }
            )

    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = (
            lineitem.category
            if (
                lineitem.category == lineitem.sub_category
                or lineitem.sub_category == None
            )
            else "{0} / {1}".format(lineitem.category, lineitem.sub_category)
        )

        category_attribute = ExpenseAttribute.objects.filter(
            value=category,
            workspace_id=expense_group.workspace_id,
            attribute_type=FyleAttributeEnum.CATEGORY,
        ).first()

        account = Mapping.objects.filter(
            source_type=FyleAttributeEnum.CATEGORY,
            source=category_attribute,
            workspace_id=expense_group.workspace_id,
        ).first()

        if not account:
            bulk_errors.append(
                {
                    "row": row,
                    "expense_group_id": expense_group.id,
                    "value": category,
                    "type": "Category Mapping",
                    "message": "Category Mapping not found",
                }
            )

            if category_attribute:
                error, created = Error.get_or_create_error_with_expense_group(expense_group, category_attribute)
                error.increase_repetition_count_by_one(created)

        row = row + 1

    if bulk_errors:
        raise BulkError("Mappings are missing", bulk_errors)


def check_expenses_reimbursement_status(expenses, workspace_id, platform, filter_credit_expenses):

    if expenses.first().paid_on_fyle:
        return True

    report_id = expenses.first().report_id

    expenses = platform.expenses.get(
        source_account_type=['PERSONAL_CASH_ACCOUNT'],
        filter_credit_expenses=filter_credit_expenses,
        report_id=report_id
    )

    is_paid = False
    if expenses:
        is_paid = expenses[0]['state'] == 'PAID'

    if is_paid:
        Expense.objects.filter(workspace_id=workspace_id, report_id=report_id, paid_on_fyle=False).update(paid_on_fyle=True, updated_at=datetime.now(timezone.utc))

    return is_paid


@handle_xero_exceptions(payment=True)
def process_payments(
    bill: Bill, workspace_id: int, task_log: TaskLog, general_mappings
):
    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(xero_credentials, workspace_id)
    with transaction.atomic():
        xero_object_task_log = TaskLog.objects.get(expense_group=bill.expense_group)

        invoice_id = xero_object_task_log.detail["Invoices"][0]["InvoiceID"]

        payment_object = Payment.create_payment(
            expense_group=bill.expense_group,
            invoice_id=invoice_id,
            account_id=general_mappings.payment_account_id,
        )

        created_payment = xero_connection.post_payment(payment_object)

        bill.payment_synced = True
        bill.paid_on_xero = True
        bill.save()

        task_log.detail = created_payment
        task_log.payment = payment_object
        task_log.xero_errors = None
        task_log.status = TaskLogStatusEnum.COMPLETE

        task_log.save()


def validate_for_skipping_payment(bill: Bill, workspace_id: int):
    task_log = TaskLog.objects.filter(task_id='PAYMENT_{}'.format(bill.expense_group.id), workspace_id=workspace_id, type='CREATING_PAYMENT').first()
    if task_log:
        now = django_timezone.now()

        if now - relativedelta(months=2) > task_log.created_at:
            bill.is_retired = True
            bill.save()
            return True

        elif now - relativedelta(months=1) > task_log.created_at and now - relativedelta(months=2) < task_log.created_at:
            # if updated_at is within 1 months will be skipped
            if task_log.updated_at > now - relativedelta(months=1):
                return True

        # If created is within 1 month
        elif now - relativedelta(months=1) < task_log.created_at:
            # Skip if updated within the last week
            if task_log.updated_at > now - relativedelta(weeks=1):
                return True

    return False


def create_payment(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)

    platform = PlatformConnector(fyle_credentials)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    filter_credit_expenses = get_filter_credit_expenses(expense_group_settings=expense_group_settings)

    bills: List[Bill] = Bill.objects.filter(
        payment_synced=False,
        expense_group__workspace_id=workspace_id,
        expense_group__fund_source=FundSourceEnum.PERSONAL,
    ).all()

    general_mappings: GeneralMapping = GeneralMapping.objects.get(
        workspace_id=workspace_id
    )

    for bill in bills:
        expense_group_reimbursement_status = check_expenses_reimbursement_status(
            bill.expense_group.expenses.all(), workspace_id=workspace_id, platform=platform, filter_credit_expenses=filter_credit_expenses
        )

        if expense_group_reimbursement_status:

            skip_payment = validate_for_skipping_payment(bill=bill, workspace_id=workspace_id)
            if skip_payment:
                continue

            task_log, _ = TaskLog.objects.update_or_create(
                workspace_id=workspace_id,
                task_id="PAYMENT_{}".format(bill.expense_group.id),
                defaults={"status": TaskLogStatusEnum.IN_PROGRESS, "type": TaskLogTypeEnum.CREATING_PAYMENT},
            )

            process_payments(bill, workspace_id, task_log, general_mappings)


def get_all_xero_bill_ids(xero_objects):
    xero_objects_details = {}

    expense_group_ids = [xero_object.expense_group_id for xero_object in xero_objects]

    task_logs = TaskLog.objects.filter(expense_group_id__in=expense_group_ids).all()

    for task_log in task_logs:
        xero_objects_details[task_log.expense_group.id] = {
            "expense_group": task_log.expense_group,
            "bill_id": task_log.detail["Invoices"][0]["InvoiceID"],
        }

    return xero_objects_details


def check_xero_object_status(workspace_id):
    try:
        xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)

        xero_connection = XeroConnector(xero_credentials, workspace_id)

        bills = Bill.objects.filter(
            expense_group__workspace_id=workspace_id,
            paid_on_xero=False,
            expense_group__fund_source=FundSourceEnum.PERSONAL,
        ).all()

        if bills:
            bill_id_map = get_all_xero_bill_ids(bills)

            for bill in bills:
                bill_object = xero_connection.get_bill(
                    bill_id_map[bill.expense_group.id]["bill_id"]
                )

                if bill_object["Invoices"][0]["Status"] == "PAID":
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
            "Xero Credentials not found for workspace_id %s",
            workspace_id,
        )

    except UnsuccessfulAuthentication:
        logger.info(
            "Xero refresh token expired for workspace_id %s",
            workspace_id,
        )
        invalidate_xero_credentials(workspace_id)


def process_reimbursements(workspace_id):
    fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
    try:
        platform = PlatformConnector(fyle_credentials=fyle_credentials)

        reports_to_be_marked = set()
        payloads = []

        report_ids = Expense.objects.filter(fund_source='PERSONAL', paid_on_fyle=False, workspace_id=workspace_id).values_list('report_id').distinct()
        for report_id in report_ids:
            report_id = report_id[0]
            expenses = Expense.objects.filter(fund_source='PERSONAL', report_id=report_id, workspace_id=workspace_id).all()
            paid_expenses = expenses.filter(paid_on_xero=True)

            all_expense_paid = False
            if len(expenses):
                all_expense_paid = len(expenses) == len(paid_expenses)

            if all_expense_paid:
                payloads.append({'id': report_id, 'paid_notify_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')})
                reports_to_be_marked.add(report_id)

        if payloads:
            mark_paid_on_fyle(platform, payloads, reports_to_be_marked, workspace_id)
    except FyleCredential.DoesNotExist:
        logger.info("Fyle credentials not found %s", workspace_id)

    except FyleInvalidTokenError:
        logger.info("Invalid Token for Fyle")

    except InternalServerError:
        logger.info('Fyle Internal Server Error occured in workspace_id: %s', workspace_id)

    except Exception as e:
        logger.exception("Error processing reimbursements", e)


def mark_paid_on_fyle(platform, payloads:dict, reports_to_be_marked, workspace_id, retry_num=10):
    try:
        logger.info('Marking reports paid on fyle for report ids - %s', reports_to_be_marked)
        logger.info('Payloads- %s', payloads)
        platform.reports.bulk_mark_as_paid(payloads)
        Expense.objects.filter(report_id__in=list(reports_to_be_marked), workspace_id=workspace_id, paid_on_fyle=False).update(paid_on_fyle=True, updated_at=datetime.now(timezone.utc))
    except Exception as e:
        error = traceback.format_exc()
        target_messages = ['Report is not in APPROVED or PAYMENT_PROCESSING State', 'Permission denied to perform this action.']
        error_response = e.response
        to_remove = set()

        for item in error_response.get('data', []):
            if item.get('message') in target_messages:
                Expense.objects.filter(report_id=item['key'], workspace_id=workspace_id, paid_on_fyle=False).update(paid_on_fyle=True, updated_at=datetime.now(timezone.utc))
                to_remove.add(item['key'])

        for report_id in to_remove:
            payloads = [payload for payload in payloads if payload['id'] != report_id]
            reports_to_be_marked.remove(report_id)

        if retry_num > 0 and payloads:
            retry_num -= 1
            logger.info('Retrying to mark reports paid on fyle, retry_num=%d', retry_num)
            mark_paid_on_fyle(platform, payloads, reports_to_be_marked, workspace_id, retry_num)

        else:
            logger.info('Retry limit reached or no payloads left. Failed to process payloads - %s:', reports_to_be_marked)

        error = {
            'error': error
        }
        logger.exception(error)


def create_missing_currency(workspace_id: int):
    """
    Create missing currency in Xero
    :param workspace_id:
    :return:
    """
    try:
        xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
        xero_connection = XeroConnector(xero_credentials, workspace_id)
        tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
        xero_connection.connection.set_tenant_id(tenant_mapping.tenant_id)

        currencies = xero_connection.connection.currencies.get_all()["Currencies"]

        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)
        my_profile = platform.connection.v1.spender.my_profile.get()
        fyle_currency = my_profile["data"]["org"]["currency"]

        existing_currency = list(
            filter(lambda currency: currency["Code"] == fyle_currency, currencies)
        )

        if not existing_currency:
            xero_connection.connection.currencies.post(
                data={"Code": fyle_currency, "Description": fyle_currency}
            )
            logger.info("Created missing currency %s in Xero", fyle_currency)

    except UnsuccessfulAuthentication:
        logger.info(
            "Xero refresh token expired for workspace_id %s",
            workspace_id,
        )
        invalidate_xero_credentials(workspace_id)

    except Exception as exception:
        logger.exception("Error creating currency in Xero", exception)


def update_xero_short_code(workspace_id: int):
    """
    Update Xero short code
    :param workspace_id:
    :return:
    """
    try:
        xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
        xero_connection = XeroConnector(xero_credentials, workspace_id)

        tenant_mapping = TenantMapping.objects.get(workspace_id=workspace_id)
        xero_connection.connection.set_tenant_id(tenant_mapping.tenant_id)
        short_code = xero_connection.connection.organisations.get_all()[0]["ShortCode"]

        workspace = Workspace.objects.get(pk=workspace_id)
        workspace.xero_short_code = short_code
        workspace.save()

        logger.info("Updated Xero short code")

    except UnsuccessfulAuthentication:
        logger.info(
            "Xero refresh token expired for workspace_id %s",
            workspace_id,
        )
        invalidate_xero_credentials(workspace_id)

    except Exception as exception:
        logger.exception("Error updating Xero short code", exception)


def generate_export_url_and_update_expense(expense_group: ExpenseGroup, export_type: str) -> None:
    """
    Generate export url and update expense
    :param expense_group: Expense Group
    :return: None
    """
    workspace = Workspace.objects.get(id=expense_group.workspace_id)
    try:
        if export_type == 'BILL':
            export_id = expense_group.response_logs['Invoices'][0]['InvoiceID']
            if workspace.xero_short_code:
                url = f'https://go.xero.com/organisationlogin/default.aspx?shortcode={workspace.xero_short_code}&redirecturl=/AccountsPayable/Edit.aspx?InvoiceID={export_id}'
            else:
                url = f'https://go.xero.com/AccountsPayable/View.aspx?invoiceID={export_id}'
        else:
            export_id = expense_group.response_logs['BankTransactions'][0]['BankTransactionID']
            account_id = expense_group.response_logs['BankTransactions'][0]['BankAccount']['AccountID']
            if workspace.xero_short_code:
                url = f'https://go.xero.com/organisationlogin/default.aspx?shortcode={workspace.xero_short_code}&redirecturl=/Bank/ViewTransaction.aspx?bankTransactionID={export_id}&accountID={account_id}'
            else:
                url = f'https://go.xero.com/Bank/ViewTransaction.aspx?bankTransactionID={export_id}&accountID={account_id}'
    except Exception as error:
        # Defaulting it to Intacct app url, worst case scenario if we're not able to parse it properly
        url = 'https://go.xero.com'
        logger.error('Error while generating export url %s', error)

    expense_group.export_url = url
    expense_group.save()

    update_complete_expenses(expense_group.expenses.all(), url)
    post_accounting_export_summary(workspace_id=workspace.id, expense_ids=[expense.id for expense in expense_group.expenses.all()], fund_source=expense_group.fund_source)
