from unittest.mock import MagicMock
from xerosdk.exceptions import UnsuccessfulAuthentication
from apps.exceptions import handle_view_exceptions


def test_handle_view_exceptions(mocker):
    workspace_id = 123

    mocked_patch = MagicMock()
    mocker.patch('apps.exceptions.patch_integration_settings', side_effect=mocked_patch)

    @handle_view_exceptions()
    def func(*args, **kwargs):
        raise UnsuccessfulAuthentication('Invalid Token')

    func(workspace_id=workspace_id)

    args, kwargs = mocked_patch.call_args

    assert args[0] == workspace_id
    assert kwargs['is_token_expired'] == True
