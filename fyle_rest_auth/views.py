"""
Fyle Authentication views
"""
from rest_framework.views import APIView, status
from rest_framework.response import Response

from .helpers import validate_code_and_login, validate_and_refresh_token


class LoginView(APIView):
    """
    Login Using Fyle Account
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Login using authorization code
        """
        tokens = validate_code_and_login(request)

        return Response(
            data=tokens,
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    """
    Refresh Access Token
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        tokens = validate_and_refresh_token(request)

        return Response(
            data=tokens,
            status=status.HTTP_200_OK
        )
