from .base import Base
from datetime import datetime
import logging
from fyle_accounting_mappings.models import ExpenseAttributesDeletionCache

logger = logging.getLogger(__name__)
logger.level = logging.INFO

class Projects(Base):
    """Class for Projects APIs."""

    def __init__(self):
        Base.__init__(self, attribute_type='PROJECT')


    def sync(self, sync_after: datetime = None):
        """
        Syncs the latest API data to DB.
        """
        try:
            expense_attributes_deletion_cache, _ = ExpenseAttributesDeletionCache.objects.get_or_create(workspace_id=self.workspace_id)
            generator = self.get_all_generator()

            for items in generator:
                project_attributes = []
                expense_attributes_deletion_cache = ExpenseAttributesDeletionCache.objects.get(workspace_id=self.workspace_id)
                for project in items['data']:
                    expense_attributes_deletion_cache.project_ids.append(project['id'])
                    
                    if self.attribute_is_valid(project):
                        if project['sub_project']:
                            project['name'] = '{0} / {1}'.format(project['name'], project['sub_project'])

                        project_attributes.append({
                            'attribute_type': self.attribute_type,
                            'display_name': self.attribute_type.replace('_', ' ').title(),
                            'value': project['name'],
                            'active': project['is_enabled'],
                            'source_id': project['id']
                        })

                expense_attributes_deletion_cache.save()
                self.bulk_create_or_update_expense_attributes(project_attributes, True)
            
            self.bulk_update_deleted_expense_attributes()

        except Exception as exception:
            logger.exception(exception)
            expense_attributes_deletion_cache = ExpenseAttributesDeletionCache.objects.get(workspace_id=self.workspace_id)
            expense_attributes_deletion_cache.project_ids = []
            expense_attributes_deletion_cache.save()
            
