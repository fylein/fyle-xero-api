import logging

from rest_framework.views import status
from rest_framework.response import Response

from xerosdk.exceptions import InvalidGrant, InvalidTokenError, UnsuccessfulAuthentication, \
    WrongParamsError, InvalidClientError, InternalServerError
from apps.workspaces.models import XeroCredentials, Workspace, FyleCredential, \
    WorkspaceGeneralSettings, WorkspaceSchedule
from apps.fyle.models import ExpenseGroup
from apps.mappings.models import GeneralMapping, TenantMapping

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_view_exceptions():
    def decorator(func):
        def new_fn(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ExpenseGroup.DoesNotExist:
                return Response(
                    data={
                        'message': 'Expense group not found'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except FyleCredential.DoesNotExist:
                return Response(
                    data={
                        'message': 'Fyle credentials not found in workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except GeneralMapping.DoesNotExist:
                return Response(
                    {
                        'message': 'General mappings do not exist for the workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except (WrongParamsError, InvalidTokenError) as exception:
                logger.info('Xero token expired workspace_id - %s %s', kwargs['workspace_id'],
                            {'error': exception.response})
                return Response(
                    data={
                        'message': 'Xero token expired workspace_id'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        

            except Workspace.DoesNotExist:
                return Response(
                    data={
                        'message': 'Workspace with this id does not exist'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


            except WorkspaceSchedule.DoesNotExist:
                return Response(
                    data={
                        'message': 'Workspace schedule does not exist in workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except (InvalidGrant, UnsuccessfulAuthentication, InvalidClientError) as exception:
                logger.info(exception)
                return Response(
                    data={
                        'message': 'Xero connection expired'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except WorkspaceGeneralSettings.DoesNotExist:
                return Response(
                    {
                        'message': 'General Settings does not exist in workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


            except XeroCredentials.DoesNotExist:
                logger.info('Xero credentials not found in workspace')
                return Response(
                    data={
                        'message': 'Xero credentials not found in workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except TenantMapping.DoesNotExist:
                return Response(
                    {
                        'message': 'Tenant mappings do not exist for the workspace'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            except InternalServerError as exception:
                return Response(
                {
                    'message': 'Internal server error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            except Exception as exception:
                logger.exception(exception)
                return Response(
                    data={
                        'message': 'An unhandled error has occurred, please re-try later'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return new_fn

    return decorator
