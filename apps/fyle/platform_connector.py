from django.conf import settings

from fyle_integrations_platform_connector import PlatformConnector as PlatformIntegrationsConnector

from apps.workspaces.models import FyleCredential

from .helpers import store_cluster_domain


class PlatformConnector:
    """
    This class is responsible for connecting to Fyle Platform and fetching data from Fyle Platform and syncing to db.
    """

    def __init__(self, fyle_credentials: FyleCredential, workspace_id=None):
        """
        Initialize the Platform Integration connector
        """
        if not fyle_credentials.cluster_domain:
            fyle_credentials = store_cluster_domain(fyle_credentials)

        self.connector = PlatformIntegrationsConnector(
            cluster_domain=fyle_credentials.cluster_domain, token_url=settings.FYLE_TOKEN_URI,
            client_id=settings.FYLE_CLIENT_ID, client_secret=settings.FYLE_CLIENT_SECRET,
            refresh_token=fyle_credentials.refresh_token, workspace_id=workspace_id
        )
