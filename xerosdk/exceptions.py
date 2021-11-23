"""
Xero SDK exceptions
"""


class XeroSDKError(Exception):
    """
    The base exception class for Xero SDK
    """

    def __init__(self, msg, response=None):
        super(XeroSDKError, self).__init__(msg)
        self.message = msg
        self.response = response

    def __str__(self):
        return repr(self.message)


class InvalidClientError(XeroSDKError):
    """Invalid client ID or client secret or refresh token, 400 error."""


class InvalidGrant(XeroSDKError):
    """Invalid refresh token, 400 error."""


class UnsupportedGrantType(XeroSDKError):
    """Invalid or non-existing grant type in request body, 400 error."""


class InvalidTokenError(XeroSDKError):
    """Invalid or non-existing access token, 401 error"""


class UnsuccessfulAuthentication(XeroSDKError):
    """Invalid xero tenant ID or xero-tenant-id header missing"""


class WrongParamsError(XeroSDKError):
    """Xero validation exception occurred, 400 error"""


class NoPrivilegeError(XeroSDKError):
    """The user has insufficient privilege, 403 error."""


class NotFoundItemError(XeroSDKError):
    """Not found the item from URL, 404 error."""


class RateLimitError(XeroSDKError):
    """Rate limit exceeded, 429 error."""


class InternalServerError(XeroSDKError):
    """Internal server error, 500 error"""
