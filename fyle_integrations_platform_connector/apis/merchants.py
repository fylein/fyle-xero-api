from apps.workspaces.models import Workspace
from .base import Base
from typing import List
from fyle_accounting_mappings.models import ExpenseAttribute

class Merchants(Base):
    """
    Class for Merchants API
    """
    def __init__(self):
        Base.__init__(self, attribute_type='MERCHANT', query_params={'column_name':'eq.merchant'})

    def get(self):
        generator = self.get_all_generator()
        for items in generator:
            merchants = items['data'][0]
        
        return merchants

    def post(self, payload: List[str], skip_existing_merchants: bool = False):
        """
        Post data to Fyle 
        """
        generator = self.get_all_generator()
        for items in generator:
            merchants = items['data'][0]
            if skip_existing_merchants:
                merchants['options'] = payload
            else:
                merchants['options'].extend(payload)
            merchant_payload = { 
                'id': merchants['id'],
                'field_name': merchants['field_name'],
                'type': 'SELECT',
                'options': merchants['options'],
                'placeholder': merchants['placeholder'],
                'category_ids': merchants['category_ids'],
                'is_enabled': merchants['is_enabled'],
                'is_custom': merchants['is_custom'],
                'is_mandatory': merchants['is_mandatory'],
                'code': merchants['code'],
                'default_value': merchants['default_value'] if merchants['default_value'] else '',
            }

        return self.connection.post({'data': merchant_payload})


    def sync(self):
        """
        Syncs the latest API data to DB.
        """
        generator = self.get_all_generator()
        for items in generator:
            merchants=items['data'][0]
            existing_merchants = ExpenseAttribute.objects.filter(
                attribute_type='MERCHANT', workspace_id=self.workspace_id)
            delete_merchant_ids = []

            if(existing_merchants):
                for existing_merchant in existing_merchants:
                    if existing_merchant.value not in merchants['options']:
                        delete_merchant_ids.append(existing_merchant.id)
                    
                ExpenseAttribute.objects.filter(id__in=delete_merchant_ids).delete()

            merchant_attributes = []

            for option in merchants['options']:
                merchant_attributes.append({
                    'attribute_type': 'MERCHANT',
                    'display_name': 'Merchant',
                    'value': option,
                    'active': True,
                    'source_id': merchants['id'],
                })

            self.bulk_create_or_update_expense_attributes(merchant_attributes, True)
