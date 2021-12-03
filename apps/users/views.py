from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from fyle_rest_auth.models import AuthToken
from fyle_integrations_platform_connector import PlatformConnector

from apps.workspaces.models import FyleCredential

from apps.fyle.utils import FyleConnector
from apps.fyle.helpers import get_cluster_domain, get_fyle_orgs

class UserProfileView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get User Details
        """
        print('request.user', request.user)
        fyle_credentials = FyleCredential.objects.filter(workspace__user=request.user).first()
        print('fyle_credentials',fyle_credentials)

        if not fyle_credentials:
            refresh_token = AuthToken.objects.get(user__user_id=request.user).refresh_token
            cluster_domain = get_cluster_domain(refresh_token)

            fyle_credentials = FyleCredential(
                cluster_domain=cluster_domain,
                refresh_token=refresh_token
            )

        platform = PlatformConnector(fyle_credentials)
        employee_profile = platform.connection.v1beta.spender.my_profile.get()

        return Response(
            data=employee_profile,
            status=status.HTTP_200_OK
        )


class FyleOrgsView(generics.ListCreateAPIView):
    """
    FyleOrgs view
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get cluster domain from Fyle
        """
        fyle_credentials = AuthToken.objects.get(user__user_id=request.user)
        fyle_orgs = get_fyle_orgs(fyle_credentials.refresh_token)

        return Response(
            data=fyle_orgs,
            status=status.HTTP_200_OK
        )
