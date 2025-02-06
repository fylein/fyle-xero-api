from unittest.mock import MagicMock
from xerosdk.exceptions import NoPrivilegeError
from apps.xero.exceptions import handle_xero_exceptions


def test_handle_view_exceptions(mocker, db):
    workspace_id = 1
    task_log_id = 1

    mocked_patch = MagicMock()
    mocker.patch('apps.xero.exceptions.patch_integration_settings', side_effect=mocked_patch)

    @handle_xero_exceptions(payment=False)
    def func(expense_group_id: int, task_log_id: int, xero_connection):
        raise NoPrivilegeError('Invalid Token')

    func(workspace_id, task_log_id, MagicMock())

    args, kwargs = mocked_patch.call_args

    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == True

    @handle_xero_exceptions(payment=True)
    def func2(bill, workspace_id: int, task_log):
        raise NoPrivilegeError('Invalid Token')

    func2(MagicMock(), workspace_id, MagicMock())

    args, kwargs = mocked_patch.call_args

    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == True
