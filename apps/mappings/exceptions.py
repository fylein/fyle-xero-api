import logging
import traceback

from fyle.platform.exceptions import (
    InternalServerError,
    InvalidTokenError,
    PlatformError,
    WrongParamsError,
    RetryException
)
from xerosdk.exceptions import InvalidGrant
from xerosdk.exceptions import InvalidTokenError as XeroInvalidTokenError
from xerosdk.exceptions import UnsuccessfulAuthentication
from xerosdk.exceptions import WrongParamsError as XeroWrongParamsError

from apps.workspaces.models import XeroCredentials

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_import_exceptions(task_name):
    def decorator(func):
        def new_fn(workspace_id, *args):
            error = {
                "task": task_name,
                "workspace_id": workspace_id,
                "alert": False,
                "message": None,
                "response": None,
            }

            try:
                return func(workspace_id, *args)
            except InvalidTokenError:
                error["message"] = "Invalid Fyle refresh token"

            except XeroCredentials.DoesNotExist:
                error["message"] = "Xero Credentials not found"

            except WrongParamsError as exception:
                error["message"] = exception.message
                error["response"] = exception.response
                error["alert"] = True

            except RetryException as exception:
                error["message"] = "Retry exception"
                error["response"] = exception.__dict__

            except InternalServerError as exception:
                error["message"] = "Internal server error while importing to Fyle"
                error["response"] = exception.__dict__

            except (XeroWrongParamsError, XeroInvalidTokenError) as exception:
                error["message"] = "Xero token expired"
                error["response"] = exception.__dict__

            except PlatformError as exception:
                error["message"] = "Platform error while importing to Fyle"
                error["response"] = exception.response

            except (UnsuccessfulAuthentication, InvalidGrant):
                error["message"] = "Xero refresh token is invalid"

            except Exception:
                response = traceback.format_exc()
                error["message"] = "Something went wrong"
                error["response"] = response
                error["alert"] = True

            if error["alert"]:
                logger.error(error)

            else:
                logger.info(error)

        return new_fn

    return decorator
