from .base import Base


class Departments(Base):
    """Class for Departments APIs."""

    def __init__(self):
        Base.__init__(self, attribute_type='DEPARTMENT', query_params={'is_enabled': 'eq.true'})
    
    def search_departments(self, query_params):
        """
        Get of departments filtered on query parameters
        :return: Generator
        """
        query_params['order'] = 'updated_at.desc'
        return self.connection.list_all(query_params)
