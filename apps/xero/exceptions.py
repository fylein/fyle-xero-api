import json
import logging
import traceback

from django.db.models import Q
from xerosdk.exceptions import (
    InvalidTokenError,
    NoPrivilegeError,
    RateLimitError,
    UnsuccessfulAuthentication,
    WrongParamsError,
    XeroSDKError,
)

from apps.fyle.actions import post_accounting_export_summary, update_failed_expenses
from apps.fyle.models import ExpenseGroup
from apps.tasks.enums import ErrorTypeEnum, TaskLogStatusEnum, TaskLogTypeEnum
from apps.tasks.models import Error, TaskLog
from apps.workspaces.helpers import invalidate_xero_credentials, patch_integration_settings
from apps.workspaces.models import FyleCredential, LastExportDetail, XeroCredentials
from fyle_xero_api.exceptions import BulkError

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def update_last_export_details(workspace_id):
    last_export_detail = LastExportDetail.objects.get(workspace_id=workspace_id)

    failed_exports = TaskLog.objects.filter(
        ~Q(type__in=[TaskLogTypeEnum.CREATING_PAYMENT, TaskLogTypeEnum.FETCHING_EXPENSES]),
        workspace_id=workspace_id,
        status__in=[TaskLogStatusEnum.FAILED, TaskLogStatusEnum.FATAL],
    ).count()

    filters = {
        'workspace_id': workspace_id,
        'status': 'COMPLETE'
    }

    if last_export_detail.last_exported_at:
        filters['updated_at__gt'] = last_export_detail.last_exported_at

    successful_exports = TaskLog.objects.filter(~Q(type__in=[TaskLogTypeEnum.CREATING_PAYMENT, TaskLogTypeEnum.FETCHING_EXPENSES]), **filters).count()

    last_export_detail.failed_expense_groups_count = failed_exports
    last_export_detail.successful_expense_groups_count = successful_exports
    last_export_detail.total_expense_groups_count = failed_exports + successful_exports
    last_export_detail.save()

    patch_integration_settings(workspace_id, errors=failed_exports)
    try:
        post_accounting_export_summary(workspace_id=workspace_id)
    except Exception as e:
        logger.error(f"Error posting accounting export summary: {e} for workspace id {workspace_id}")

    return last_export_detail


def handle_xero_error(exception, expense_group: ExpenseGroup, task_log: TaskLog):
    """
    Handle the xero-error and save it to Errors and TaskLogs table
    :params exception: exception
    :params expense_group: expense_group
    :params task_log: task_log
    :params export_type: export_type
    """
    if type(exception).__name__ == "RateLimitError":
        logger.info(exception.message)
        task_log.xero_errors = [
            {
                "error": {
                    "Elements": [
                        {
                            "ValidationErrors": [
                                {
                                    "Message": "Rate limit exceeded, integration will retry exports in a while"
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        error, created = Error.objects.update_or_create(
            workspace_id=expense_group.workspace_id,
            expense_group=expense_group,
            defaults={
                "type": ErrorTypeEnum.XERO_ERROR,
                "error_title": "Rate Limit Error",
                "error_detail": "Rate limit exceeded, integration will retry exports in a while",
                "is_resolved": False,
            },
        )
        error.increase_repetition_count_by_one(created)

    else:
        all_details = []
        logger.info(exception)
        detail = json.dumps(exception.__dict__)
        detail = json.loads(detail)

        all_details.append(
            {
                "expense_group_id": expense_group.id,
                "message": detail["message"]["Message"],
                "error": detail["message"],
            }
        )

        error_detail = "Something unexcepted happen"
        if (
            "Elements" in detail["message"]
            and len(detail["message"]["Elements"]) > 0
            and "ValidationErrors" in detail["message"]["Elements"][0]
            and len(detail["message"]["Elements"][0]["ValidationErrors"]) > 0
            and "Message" in detail["message"]["Elements"][0]["ValidationErrors"][0]
        ):
            error_detail = detail["message"]["Elements"][0]["ValidationErrors"][0][
                "Message"
            ]

        error, created = Error.objects.update_or_create(
            workspace_id=expense_group.workspace_id,
            expense_group=expense_group,
            defaults={
                "type": ErrorTypeEnum.XERO_ERROR,
                "error_title": detail["message"]["Message"],
                "error_detail": error_detail,
                "is_resolved": False,
            },
        )
        error.increase_repetition_count_by_one(created)

        task_log.xero_errors = all_details

    task_log.detail = None
    task_log.status = TaskLogStatusEnum.FAILED
    update_failed_expenses(expense_group.expenses.all(), False)

    task_log.save()


def handle_xero_exceptions(payment=False):
    def decorator(func):
        def new_fn(*args):
            if payment:
                workspace_id = args[1]
                expense_group = args[0].expense_group
                task_log = args[2]
            else:
                expense_group_id = args[0]
                expense_group = ExpenseGroup.objects.get(id=expense_group_id)
                task_log_id = args[1]
                task_log = TaskLog.objects.get(id=task_log_id)
                workspace_id = expense_group.workspace_id

            try:
                func(*args)

            except (FyleCredential.DoesNotExist, InvalidTokenError):
                logger.info("Fyle credentials not found %s", workspace_id)
                task_log.detail = {
                    "message": "Fyle credentials do not exist in workspace"
                }
                task_log.status = TaskLogStatusEnum.FAILED
                task_log.save()

            except WrongParamsError as exception:
                if payment:
                    logger.info(exception.message)
                    detail = exception.message
                    task_log.status = TaskLogStatusEnum.FAILED
                    task_log.detail = detail

                    task_log.save()
                else:
                    handle_xero_error(
                        exception=exception,
                        expense_group=expense_group,
                        task_log=task_log,
                    )

            except RateLimitError as exception:
                if payment:
                    logger.info(exception.message)
                    detail = exception.message
                    task_log.status = TaskLogStatusEnum.FAILED
                    task_log.detail = detail

                    task_log.save()
                else:
                    handle_xero_error(
                        exception=exception, expense_group=expense_group, task_log=task_log
                    )

            except (NoPrivilegeError, UnsuccessfulAuthentication) as exception:
                invalidate_xero_credentials(workspace_id)
                xero_credentials = XeroCredentials.objects.filter(
                    workspace_id=workspace_id
                ).first()
                xero_credentials.country = None
                xero_credentials.save()
                logger.info(exception.message)
                task_log.status = TaskLogStatusEnum.FAILED
                task_log.detail = None
                task_log.xero_errors = [
                    {
                        "error": {
                            "Elements": [
                                {
                                    "ValidationErrors": [
                                        {
                                            "Message": "Xero account got disconnected, please re-connect to Xero again"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]

                task_log.save()
                update_failed_expenses(expense_group.expenses.all(), False)

            except XeroCredentials.DoesNotExist:
                logger.info(
                    "Xero Account not connected / token expired for workspace_id %s",
                    workspace_id,
                )
                detail = {"message": "Xero Account not connected / token expired"}

                task_log.status = TaskLogStatusEnum.FAILED
                task_log.detail = detail

                task_log.save()
                update_failed_expenses(expense_group.expenses.all(), False)

            except XeroSDKError as exception:
                logger.info(exception.response)
                detail = exception.response
                task_log.status = TaskLogStatusEnum.FAILED
                task_log.detail = None
                task_log.xero_errors = detail

                task_log.save()
                update_failed_expenses(expense_group.expenses.all(), False)

            except BulkError as exception:
                logger.info(exception.response)
                detail = exception.response
                task_log.status = TaskLogStatusEnum.FAILED
                task_log.detail = detail
                task_log.save()
                update_failed_expenses(expense_group.expenses.all(), True)

            except Exception as error:
                error = traceback.format_exc()
                task_log.detail = {"error": error}
                task_log.status = TaskLogStatusEnum.FATAL
                task_log.save()
                logger.error(
                    "Something unexpected happened workspace_id: %s %s",
                    task_log.workspace_id,
                    task_log.detail,
                )
                update_failed_expenses(expense_group.expenses.all(), False)

            if not payment:
                post_accounting_export_summary(workspace_id=expense_group.workspace_id, expense_ids=[expense.id for expense in expense_group.expenses.all()], fund_source=expense_group.fund_source, is_failed=True)

            if not payment and args[-2] == True:
                update_last_export_details(workspace_id=expense_group.workspace_id)

        return new_fn

    return decorator
