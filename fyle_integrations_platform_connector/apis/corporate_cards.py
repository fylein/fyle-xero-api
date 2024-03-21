from .base import Base


class CorporateCards(Base):
    """Class for Corporate Cards APIs."""

    def __init__(self):
        Base.__init__(self, attribute_type='CORPORATE_CARD')

    def sync(self):
        """
        Syncs the latest API data to DB.
        """
        generator = self.get_all_generator()
        for items in generator:
            card_attributes = []
            unique_card_numbers = []
            for card in items['data']:
                if self.attribute_is_valid(card):
                    value = '{} - {}'.format(
                        card['bank_name'],
                        card['card_number'][-6:].replace('-', '')
                    )

                    if value not in unique_card_numbers:
                        unique_card_numbers.append(value)
                        card_attributes.append({
                            'attribute_type': self.attribute_type,
                            'display_name': self.attribute_type.replace('_', ' ').title(),
                            'value': value,
                            'source_id': card['id'],
                            'active': None,
                            'detail': {
                                'cardholder_name': card['cardholder_name']
                            }
                        })

            self.bulk_create_or_update_expense_attributes(card_attributes, True)
