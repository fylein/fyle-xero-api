from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.fyle.helpers import get_fyle_orgs
from apps.users.helpers import get_cluster_domain_and_refresh_token


class FyleOrgsView(generics.ListCreateAPIView):
    """
    FyleOrgs view
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get cluster domain from Fyle
        """
        cluster_domain, refresh_token = get_cluster_domain_and_refresh_token(
            request.user
        )

        fyle_orgs = get_fyle_orgs(refresh_token, cluster_domain)

        return Response(data=fyle_orgs, status=status.HTTP_200_OK)
