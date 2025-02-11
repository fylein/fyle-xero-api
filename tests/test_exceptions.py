from unittest.mock import MagicMock
from xerosdk.exceptions import UnsuccessfulAuthentication
from apps.exceptions import handle_view_exceptions


def test_handle_view_exceptions(mocker):
    workspace_id = 123

    mocked_invalidate_call = MagicMock()
    mocker.patch('apps.exceptions.invalidate_xero_credentials', side_effect=mocked_invalidate_call)

    @handle_view_exceptions()
    def func(*args, **kwargs):
        raise UnsuccessfulAuthentication('Invalid Token')

    func(workspace_id=workspace_id)

    args, _ = mocked_invalidate_call.call_args

    assert args[0] == workspace_id
