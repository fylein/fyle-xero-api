from typing import List

from django.db.models import Q

import django_filters


from .models import EmployeeMapping, DestinationAttribute, ExpenseAttribute

class EmployeesAutoMappingHelper:
    """
    EmployeesAutoMappingHelper is a helper class to automatically map employee names
    to employee numbers.
    """
    def __init__(self, workspace_id: int, destination_type: str, employee_mapping_preference: str = ''):
        """
        Initialize the EmployeesAutoMappingHelper class.
        """
        self.destination_type = destination_type
        self.employee_mapping_preference = employee_mapping_preference
        self.workspace_id = workspace_id
        self.destination_value_id_map = {}

    @staticmethod
    def create_mappings_and_update_flag(mapping_creation_batch: List[EmployeeMapping],
                                        mapping_updation_batch: list, update_key: str) -> None:
        """
        Create Mappings and Update Flag
        :param mapping_creation_batch: Mapping Creation Batch
        :param mapping_updation_batch: Mapping Updation Batch
        :param update_key: Update Key
        :return: created mappings
        """
        mappings = []
        expense_attributes_to_be_updated = []

        if mapping_creation_batch:
            created_mappings = EmployeeMapping.objects.bulk_create(mapping_creation_batch, batch_size=50)
            mappings.extend(created_mappings)

        if mapping_updation_batch:
            EmployeeMapping.objects.bulk_update(
                mapping_updation_batch, fields=[update_key], batch_size=50
            )
            for mapping in mapping_updation_batch:
                mappings.append(mapping)

        for mapping in mappings:
            expense_attributes_to_be_updated.append(
                ExpenseAttribute(
                    id=mapping.source_employee.id,
                    auto_mapped=True
                )
            )

        if expense_attributes_to_be_updated:
            ExpenseAttribute.objects.bulk_update(
                expense_attributes_to_be_updated, fields=['auto_mapped'], batch_size=50
            )


    def get_existing_employee_mappings(self) -> List[EmployeeMapping]:
        """
        Get Existing Employee Mappings
        :return: Existing Employee Mappings
        """
        return EmployeeMapping.objects.filter(
            workspace_id=self.workspace_id
        ).all()

    def check_name_matches(self, source_attribute: ExpenseAttribute) -> dict:
        """
        Check if the source attribute matches with the destination attribute
        :param source_attribute: Source Attribute
        :return: Destination Column and value if exact match found
        """
        source_value = ''
        destination = {}

        if self.employee_mapping_preference == 'EMAIL':
            source_value = source_attribute.value
        elif self.employee_mapping_preference == 'NAME':
            source_value = source_attribute.detail['full_name']
        elif self.employee_mapping_preference == 'EMPLOYEE_CODE':
            source_value = source_attribute.detail['employee_code']

        # Handling employee_code or full_name null case
        if not source_value:
            source_value = ''

        # Checking case insensitive exact name match
        if source_value.lower() in self.destination_value_id_map:
            if self.destination_type == 'EMPLOYEE':
                destination['destination_employee_id'] = self.destination_value_id_map[source_value.lower()]
            elif self.destination_type == 'VENDOR':
                destination['destination_vendor_id'] = self.destination_value_id_map[source_value.lower()]
            elif self.destination_type == 'CREDIT_CARD_ACCOUNT' or self.destination_type == 'CHARGE_CARD_NUMBER':
                destination['destination_card_account_id'] = self.destination_value_id_map[source_value.lower()]

        return destination


    def construct_existing_employee_mappings_map(self) -> dict:
        """
        Construct Existing Employee Mappings Map
        :return: Existing Employee Mappings Map
        """
        existing_employee_mappings = self.get_existing_employee_mappings()
        existing_employee_mappings_map = {employee_mapping.source_employee_id: employee_mapping.id \
            for employee_mapping in existing_employee_mappings}

        return existing_employee_mappings_map


    def construct_mapping_payload(self, employee_source_attributes: List[ExpenseAttribute]
                                 ) -> (List[EmployeeMapping], list, str):
        """
        Construct mapping payload
        :param employee_source_attributes: Employee Source Attributes
        :return: mapping_creation_batch, mapping_updation_batch, update_key
        """
        mapping_creation_batch = []
        mapping_updation_batch = []
        update_key = None

        existing_employee_mappings_map = self.construct_existing_employee_mappings_map()

        for source_attribute in employee_source_attributes:
            destination = self.check_name_matches(source_attribute)

            if destination:
                update_key = list(destination.keys())[0]
                if source_attribute.id in existing_employee_mappings_map:
                    # If employee mapping row exists, then update it
                    mapping_updation_batch.append(
                        EmployeeMapping(
                            id=existing_employee_mappings_map[source_attribute.id],
                            source_employee=source_attribute,
                            **destination
                        )
                    )
                else:
                    # If employee mapping row does not exist, then create it
                    mapping_creation_batch.append(
                        EmployeeMapping(
                            source_employee_id=source_attribute.id,
                            workspace_id=self.workspace_id,
                            **destination
                        )
                    )

        return mapping_creation_batch, mapping_updation_batch, update_key


    def get_unmapped_destination_attributes(self) -> list:
        """
        Get Unmapped Destination Attributes
        :return: Unmapped Destination Attributes
        """
        destination_filter = {
            'attribute_type': self.destination_type,
            'workspace_id': self.workspace_id
        }

        if self.destination_type == 'EMPLOYEE':
            destination_filter['destination_employee__isnull'] = True
        elif self.destination_type == 'VENDOR':
            destination_filter['destination_vendor__isnull'] = True

        return DestinationAttribute.objects.filter(
            **destination_filter
        ).values('id', 'value', 'detail')


    def get_unmapped_source_attributes(self) -> List[EmployeeMapping]:
        """
        Get Unmapped Source Attributes
        :return: Unmapped Source Attributes
        """
        source_filter = {
            'attribute_type': 'EMPLOYEE',
            'workspace_id': self.workspace_id
        }

        # Filtering only not mapped expense attributes
        if self.destination_type == 'VENDOR':
            source_filter['employeemapping__destination_vendor__isnull'] = True
        elif self.destination_type == 'EMPLOYEE':
            source_filter['employeemapping__destination_employee__isnull'] = True
        elif self.destination_type == 'CREDIT_CARD_ACCOUNT' or self.destination_type == 'CHARGE_CARD_NUMBER':
            source_filter['employeemapping__destination_card_account__isnull'] = True

        employee_source_attributes_count = ExpenseAttribute.objects.filter(**source_filter).count()
        page_size = 200
        employee_source_attributes = []

        for offset in range(0, employee_source_attributes_count, page_size):
            limit = offset + page_size
            paginated_employee_source_attributes = ExpenseAttribute.objects.filter(**source_filter)[offset:limit]
            employee_source_attributes.extend(paginated_employee_source_attributes)

        return employee_source_attributes


    def set_destination_value_id_map(self, destination_attributes: list) -> dict:
        """
        Construct Destination Value ID Map
        :param destination_attributes: Destination Attributes
        :return: Destination Value ID Map
        """
        for destination_attribute in destination_attributes:
            value_to_be_appended = None
            if self.employee_mapping_preference == 'EMAIL' and destination_attribute['detail'] \
                    and destination_attribute['detail']['email']:
                value_to_be_appended = destination_attribute['detail']['email'].replace('*', '')
            elif self.employee_mapping_preference in ['NAME', 'EMPLOYEE_CODE']:
                value_to_be_appended = destination_attribute['value'].replace('*', '')

            if value_to_be_appended:
                self.destination_value_id_map[value_to_be_appended.lower()] = destination_attribute['id']


    def reimburse_mapping(self) -> None:
        """
        Auto map employees
        :param destination_type: Destination Type of mappings
        :param employee_mapping_preference: Employee Mapping Preference
        :param workspace_id: Workspace ID
        """
        # Get unmapped destination attributes
        destination_attributes = self.get_unmapped_destination_attributes()

        # Set destination value id map
        self.set_destination_value_id_map(destination_attributes)

        # Get unmapped source attributes
        employee_source_attributes = self.get_unmapped_source_attributes()

        mapping_creation_batch, mapping_updation_batch, update_key = self.construct_mapping_payload(
            employee_source_attributes
        )

        self.create_mappings_and_update_flag(mapping_creation_batch, mapping_updation_batch, update_key)

    def ccc_mapping(self, default_ccc_account_id: str, attribute_type: str = None):
        """
        Auto map ccc employees
        :param default_ccc_account_id: Default CCC Account ID
        :param attribute_type: destination attribute type
        """
        mapping_creation_batch = []
        mapping_updation_batch = []

        # Get unmapped source attributes
        employee_source_attributes = self.get_unmapped_source_attributes()

        default_destination_attribute = DestinationAttribute.objects.filter(
            destination_id=default_ccc_account_id, workspace_id=self.workspace_id,
            attribute_type=attribute_type if attribute_type else 'CREDIT_CARD_ACCOUNT'
        ).first()

        existing_employee_mappings_map = self.construct_existing_employee_mappings_map()

        for source_employee in employee_source_attributes:
            if source_employee.id in existing_employee_mappings_map:
                # If employee mapping row exists, then update it
                mapping_updation_batch.append(
                    EmployeeMapping(
                        id=existing_employee_mappings_map[source_employee.id],
                        destination_card_account_id=default_destination_attribute.id
                    )
                )
            else:
                # If employee mapping row does not exist, then create it
                mapping_creation_batch.append(
                    EmployeeMapping(
                        source_employee_id=source_employee.id,
                        destination_card_account_id=default_destination_attribute.id,
                        workspace_id=self.workspace_id
                    )
                )

        if mapping_creation_batch:
            EmployeeMapping.objects.bulk_create(mapping_creation_batch, batch_size=50)

        if mapping_updation_batch:
            EmployeeMapping.objects.bulk_update(
                mapping_updation_batch, fields=['destination_card_account_id'], batch_size=50
            )


class ExpenseAttributeFilter(django_filters.FilterSet):
    mapping_source_alphabets = django_filters.CharFilter(method='filter_mapping_source_alphabets')
    value = django_filters.CharFilter(field_name='value', lookup_expr='icontains')

    def filter_mapping_source_alphabets(self, queryset, name, value):
        if value:
            queryset = queryset.filter(Q(value__istartswith=value))
        return queryset

    class Meta:
        model = ExpenseAttribute
        fields = ['mapping_source_alphabets', 'value']
