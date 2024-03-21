from .base import Base


class ExpenseCustomFields(Base):
    """Class for Expense Custom Fields APIs."""

    def sync(self):
        """
        Syncs the latest API data to DB.
        """
        query_params = {'order': 'updated_at.desc', 'is_custom': 'eq.true', 'type': 'eq.SELECT', 'is_enabled': 'eq.true'}
        generator = self.connection.list_all(query_params)

        for items in generator:
            for row in items['data']:
                if self.attribute_is_valid(row):
                    attributes = []
                    count = 1
                    attribute_type = row['field_name'].upper().replace(' ', '_')
                    for option in row['options']:
                        attributes.append({
                            'attribute_type': attribute_type,
                            'display_name': row['field_name'],
                            'value': option,
                            'active': True,
                            'source_id': 'expense_custom_field.{}.{}'.format(row['field_name'].lower(), count),
                            'detail': {
                                'custom_field_id': row['id'],
                                'placeholder': row['placeholder'],
                                'is_mandatory': row['is_mandatory'],
                                'is_dependent': False
                            }
                        })
                        count = count + 1
                    self.attribute_type = attribute_type
                    self.bulk_create_or_update_expense_attributes(attributes, True)

    def list_all(self, query_params=None):
        """
        List all the custom fields
        """
        if not query_params:
            query_params = {'order': 'updated_at.desc', 'is_custom': 'eq.true', 'is_enabled': 'eq.true'}
        generator = self.connection.list_all(query_params)
        custom_fields = []

        for items in generator:
            custom_fields = items['data']

        return custom_fields
