from .base import Base

class Subscriptions(Base):
    """
    Class for Subscriptions API
    """

    def __init__(self):
        Base.__init__(self, query_params={'order': 'id.asc'})
