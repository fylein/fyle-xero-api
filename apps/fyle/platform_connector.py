from django.conf import settings

from fyle_integrations_platform_connector import PlatformConnector as PlatformIntegrationsConnector

from apps.workspaces.models import FyleCredential

from .utils import FyleConnector


class PlatformConnector:
    """
    This class is responsible for connecting to Fyle Platform and fetching data from Fyle Platform and syncing to db.
    """

    def __init__(self, fyle_credentials: FyleCredential, workspace_id=None):
        """
        Initialize the Platform Integration connector
        """
        if not fyle_credentials.cluster_domain:
            fyle_credentials = self.__store_cluster_domain(fyle_credentials)

        self.connector = PlatformIntegrationsConnector(
            cluster_domain=fyle_credentials.cluster_domain, token_url=settings.FYLE_TOKEN_URI,
            client_id=settings.FYLE_CLIENT_ID, client_secret=settings.FYLE_CLIENT_SECRET,
            refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id
        )

    @staticmethod
    def __store_cluster_domain(fyle_credentials: FyleCredential) -> FyleCredential:
        """
        Get or store cluster domain.
        """
        fyle_connector = FyleConnector(fyle_credentials.refresh_token)
        cluster_domain = fyle_connector.get_cluster_domain()['cluster_domain']
        fyle_credentials.cluster_domain = cluster_domain
        fyle_credentials.save()

        return fyle_credentials
