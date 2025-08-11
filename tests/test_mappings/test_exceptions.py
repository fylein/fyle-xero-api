from fyle.platform.exceptions import InternalServerError, InvalidTokenError, WrongParamsError
from xerosdk.exceptions import InvalidTokenError as XeroInvalidTokenError
from xerosdk.exceptions import UnsuccessfulAuthentication
from xerosdk.exceptions import WrongParamsError as XeroWrongParamsError

from apps.mappings.exceptions import handle_import_exceptions_v2
from apps.workspaces.models import XeroCredentials
from apps.xero.utils import XeroConnector
from fyle_integrations_imports.models import ImportLog
from fyle_integrations_imports.modules.projects import Project


def test_handle_import_exceptions(db, create_temp_workspace, add_xero_credentials, add_fyle_credentials):
    workspace_id = 3
    ImportLog.objects.create(
        workspace_id=workspace_id,
        status = 'IN_PROGRESS',
        attribute_type = 'PROJECT',
        total_batches_count = 10,
        processed_batches_count = 2,
        error_log = []
    )
    xero_credentials = XeroCredentials.get_active_xero_credentials(workspace_id)
    xero_connection = XeroConnector(credentials_object=xero_credentials, workspace_id=workspace_id)

    import_log = ImportLog.objects.get(workspace_id=workspace_id, attribute_type='PROJECT')
    project = Project(workspace_id, 'CUSTOMER', None,  xero_connection, 'customers', True)

    # WrongParamsError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise WrongParamsError('This is WrongParamsError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'This is WrongParamsError'
    assert import_log.error_log['alert'] == True

    # FyleInvalidTokenError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise InvalidTokenError('This is FyleInvalidTokenError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid Token for fyle'
    assert import_log.error_log['alert'] == False

    # InternalServerError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise InternalServerError('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Internal server error while importing to Fyle'
    assert import_log.error_log['alert'] == True

    # XeroWrongParamsError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise XeroWrongParamsError('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Something went wrong'
    assert import_log.error_log['alert'] == True

    # XeroInvalidTokenError
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise XeroInvalidTokenError('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid Token or Xero credentials does not exist workspace_id - 3'
    assert import_log.error_log['alert'] == False

    # XeroCredentials.DoesNotExist
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise XeroCredentials.DoesNotExist('This is InternalServerError')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid Token or Xero credentials does not exist workspace_id - 3'
    assert import_log.error_log['alert'] == False

    # Exception
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise UnsuccessfulAuthentication('Invalid xero tenant ID')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FAILED'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Invalid xero tenant ID or xero-tenant-id header missing in workspace_id - 3'
    assert import_log.error_log['alert'] == False

    # Exception
    @handle_import_exceptions_v2
    def to_be_decoreated(expense_attribute_instance, import_log):
        raise Exception('This is a general Exception')

    to_be_decoreated(project, import_log)

    assert import_log.status == 'FATAL'
    assert import_log.error_log['task'] == 'Import PROJECT to Fyle and Auto Create Mappings'
    assert import_log.error_log['message'] == 'Something went wrong'
    assert import_log.error_log['alert'] == False
