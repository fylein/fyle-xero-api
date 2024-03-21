from .base import Base


class Employees(Base):
    """Class for Employees APIs."""

    def __init__(self):
        Base.__init__(self, attribute_type='EMPLOYEE', query_params={'is_enabled': 'eq.true'})

    def get_employee_by_email(self, email: str):
        """
        Get employee by email
        """
        return self.connection.list({
            'user->email': 'eq.{}'.format(email),
            'offset': 0,
            'limit': 1,
            'order': 'updated_at.desc'
        })['data']

    def get_admins(self):
        """
        Get admins of the org
        """
        admins = []
        generator = self.connection.list_all({
            'roles': 'like.%ADMIN%',
            'order': 'updated_at.desc'
        })

        for items in generator:
            for employee in items['data']:
                admins.append({
                    'user_id': employee['user']['id'],
                    'email': employee['user']['email'],
                    'full_name': employee['user']['full_name'],
                })

        return admins

    def sync(self):
        """
        Syncs the latest API data to DB.
        """
        generator = self.get_all_generator()
        for items in generator:
            employee_attributes = []
            for employee in items['data']:
                if self.attribute_is_valid(employee):
                    employee_attributes.append({
                        'attribute_type': self.attribute_type,
                        'display_name': self.attribute_type.replace('_', ' ').title(),
                        'value': employee['user']['email'],
                        'source_id': employee['id'],
                        'active': True,
                        'detail': {
                            'user_id': employee['user_id'],
                            'employee_code': employee['code'],
                            'full_name': employee['user']['full_name'],
                            'location': employee['location'],
                            'department': employee['department']['name'] if employee['department'] else None,
                            'department_id': employee['department_id'],
                            'department_code': employee['department']['code'] if employee['department'] else None
                        }
                    })

            self.bulk_create_or_update_expense_attributes(employee_attributes, True)
