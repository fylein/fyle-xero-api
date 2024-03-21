from .base import Base
import logging
from datetime import datetime
from fyle_accounting_mappings.models import ExpenseAttributesDeletionCache

logger = logging.getLogger(__name__)
logger.level = logging.INFO

class Categories(Base):
    """Class for Categories APIs."""

    def __init__(self):
        Base.__init__(self, attribute_type='CATEGORY')

    def sync(self, sync_after: datetime = None):
        """
        Syncs the latest API data to DB.
        """
        try:
            expense_attributes_deletion_cache, _ = ExpenseAttributesDeletionCache.objects.get_or_create(workspace_id=self.workspace_id)
            generator = self.get_all_generator()
            
            for items in generator:
                category_attributes = []
                expense_attributes_deletion_cache = ExpenseAttributesDeletionCache.objects.get(workspace_id=self.workspace_id)
                for category in items['data']:
                    expense_attributes_deletion_cache.category_ids.append(category['id'])
                    if self.attribute_is_valid(category):
                        if category['sub_category'] and category['name'] != category['sub_category']:
                            category['name'] = '{0} / {1}'.format(category['name'], category['sub_category'])

                        category_attributes.append({
                            'attribute_type': self.attribute_type,
                            'display_name': self.attribute_type.replace('_', ' ').title(),
                            'value': category['name'],
                            'source_id': category['id'],
                            'active': category['is_enabled'],
                            'detail': None
                        })

                expense_attributes_deletion_cache.save()
                self.bulk_create_or_update_expense_attributes(category_attributes, True)

            self.bulk_update_deleted_expense_attributes()

        except Exception as exception:
            logger.exception(exception)
            expense_attributes_deletion_cache = ExpenseAttributesDeletionCache.objects.get(workspace_id=self.workspace_id)
            expense_attributes_deletion_cache.category_ids = []
            expense_attributes_deletion_cache.save()
