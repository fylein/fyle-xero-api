import importlib
from typing import List, Dict
from datetime import datetime
from django.db import models, transaction
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

from .exceptions import BulkError
from .utils import assert_valid


workspace_models = importlib.import_module("apps.workspaces.models")
Workspace = workspace_models.Workspace


def validate_mapping_settings(mappings_settings: List[Dict]):
    bulk_errors = []

    row = 0

    for mappings_setting in mappings_settings:
        if ('source_field' not in mappings_setting) and (not mappings_setting['source_field']):
            bulk_errors.append({
                'row': row,
                'value': None,
                'message': 'source field cannot be empty'
            })

        if ('destination_field' not in mappings_setting) and (not mappings_setting['destination_field']):
            bulk_errors.append({
                'row': row,
                'value': None,
                'message': 'destination field cannot be empty'
            })

        row = row + 1

    if bulk_errors:
        raise BulkError('Errors while creating settings', bulk_errors)


def create_mappings_and_update_flag(mapping_batch: list, set_auto_mapped_flag: bool = True, **kwargs):
    model_type = kwargs['model_type'] if 'model_type' in kwargs else Mapping
    if model_type == CategoryMapping:
        mappings = CategoryMapping.objects.bulk_create(mapping_batch, batch_size=50)
    else:
        mappings = Mapping.objects.bulk_create(mapping_batch, batch_size=50)

    if set_auto_mapped_flag:
        expense_attributes_to_be_updated = []

        for mapping in mappings:
            expense_attributes_to_be_updated.append(
                ExpenseAttribute(
                    id=mapping.source_category.id if model_type == CategoryMapping else mapping.source.id,
                    auto_mapped=True
                )
            )

        if expense_attributes_to_be_updated:
            ExpenseAttribute.objects.bulk_update(
                expense_attributes_to_be_updated, fields=['auto_mapped'], batch_size=50)

    return mappings


def construct_mapping_payload(employee_source_attributes: list, employee_mapping_preference: str,
                              destination_id_value_map: dict, destination_type: str, workspace_id: int):
    existing_source_ids = get_existing_source_ids(destination_type, workspace_id)

    mapping_batch = []
    for source_attribute in employee_source_attributes:
        # Ignoring already present mappings
        if source_attribute.id not in existing_source_ids:
            if employee_mapping_preference == 'EMAIL':
                source_value = source_attribute.value
            elif employee_mapping_preference == 'NAME':
                source_value = source_attribute.detail['full_name']
            elif employee_mapping_preference == 'EMPLOYEE_CODE':
                source_value = source_attribute.detail['employee_code']

            # Checking exact match
            if source_value.lower() in destination_id_value_map:
                destination_id = destination_id_value_map[source_value.lower()]
                mapping_batch.append(
                    Mapping(
                        source_type='EMPLOYEE',
                        destination_type=destination_type,
                        source_id=source_attribute.id,
                        destination_id=destination_id,
                        workspace_id=workspace_id
                    )
                )

    return mapping_batch


def get_existing_source_ids(destination_type: str, workspace_id: int):
    existing_mappings = Mapping.objects.filter(
        source_type='EMPLOYEE', destination_type=destination_type, workspace_id=workspace_id
    ).all()

    existing_source_ids = []
    for mapping in existing_mappings:
        existing_source_ids.append(mapping.source.id)

    return existing_source_ids


class ExpenseAttributesDeletionCache(models.Model):
    id = models.AutoField(primary_key=True)
    category_ids = ArrayField(default=[], base_field=models.CharField(max_length=255))
    project_ids = ArrayField(default=[], base_field=models.CharField(max_length=255))
    workspace = models.OneToOneField(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')

    class Meta:
        db_table = 'expense_attributes_deletion_cache'


class ExpenseAttribute(models.Model):
    """
    Fyle Expense Attributes
    """
    id = models.AutoField(primary_key=True)
    attribute_type = models.CharField(max_length=255, help_text='Type of expense attribute')
    display_name = models.CharField(max_length=255, help_text='Display name of expense attribute')
    value = models.CharField(max_length=1000, help_text='Value of expense attribute')
    source_id = models.CharField(max_length=255, help_text='Fyle ID')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    auto_mapped = models.BooleanField(default=False, help_text='Indicates whether the field is auto mapped or not')
    auto_created = models.BooleanField(default=False,
                                       help_text='Indicates whether the field is auto created by the integration')
    active = models.BooleanField(null=True, help_text='Indicates whether the fields is active or not')
    detail = JSONField(help_text='Detailed expense attributes payload', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'expense_attributes'
        unique_together = ('value', 'attribute_type', 'workspace')

    @staticmethod
    def create_or_update_expense_attribute(attribute: Dict, workspace_id):
        """
        Get or create expense attribute
        """
        expense_attribute, _ = ExpenseAttribute.objects.update_or_create(
            attribute_type=attribute['attribute_type'],
            value=attribute['value'],
            workspace_id=workspace_id,
            defaults={
                'active': attribute['active'] if 'active' in attribute else None,
                'source_id': attribute['source_id'],
                'display_name': attribute['display_name'],
                'detail': attribute['detail'] if 'detail' in attribute else None
            }
        )
        return expense_attribute

    @staticmethod
    def bulk_update_deleted_expense_attributes(attribute_type: str, workspace_id: int):
        """
        Bulk update deleted expense attributes
        :param attribute_type: Attribute type
        :param workspace_id: Workspace Id
        """
        expense_attributes_deletion_cache = ExpenseAttributesDeletionCache.objects.get(workspace_id=workspace_id)
        attributes_to_be_updated = []

        if attribute_type == 'CATEGORY':
            deleted_attributes = ExpenseAttribute.objects.filter(
                attribute_type=attribute_type, workspace_id=workspace_id, active=True
            ).exclude(source_id__in=expense_attributes_deletion_cache.category_ids)
            expense_attributes_deletion_cache.category_ids = []
            expense_attributes_deletion_cache.save()
        else:
            deleted_attributes = ExpenseAttribute.objects.filter(
                attribute_type=attribute_type, workspace_id=workspace_id, active=True
            ).exclude(source_id__in=expense_attributes_deletion_cache.project_ids)
            expense_attributes_deletion_cache.project_ids = []
            expense_attributes_deletion_cache.save()

        for attribute in deleted_attributes:
            attributes_to_be_updated.append(
                ExpenseAttribute(
                    id=attribute.id,
                    active=False,
                    updated_at=datetime.now()
                )
            )

        if attributes_to_be_updated:
            ExpenseAttribute.objects.bulk_update(
                attributes_to_be_updated, fields=['active', 'updated_at'], batch_size=50)

    @staticmethod
    def bulk_create_or_update_expense_attributes(
            attributes: List[Dict], attribute_type: str, workspace_id: int, update: bool = False):
        """
        Create Expense Attributes in bulk
        :param update: Update Pre-existing records or not
        :param attribute_type: Attribute type
        :param attributes: attributes = [{
            'attribute_type': Type of attribute,
            'display_name': Display_name of attribute_field,
            'value': Value of attribute,
            'source_id': Fyle Id of the attribute,
            'detail': Extra Details of the attribute
        }]
        :param workspace_id: Workspace Id
        :return: created / updated attributes
        """
        attribute_value_list = [attribute['value'] for attribute in attributes]

        existing_attributes = ExpenseAttribute.objects.filter(
            value__in=attribute_value_list, attribute_type=attribute_type,
            workspace_id=workspace_id).values('id', 'value', 'detail', 'active')

        existing_attribute_values = []

        primary_key_map = {}

        for existing_attribute in existing_attributes:
            existing_attribute_values.append(existing_attribute['value'])
            primary_key_map[existing_attribute['value']] = {
                'id': existing_attribute['id'],
                'detail': existing_attribute['detail'],
                'active': existing_attribute['active']
            }

        attributes_to_be_created = []
        attributes_to_be_updated = []

        values_appended = []
        for attribute in attributes:
            if attribute['value'] not in existing_attribute_values and attribute['value'] not in values_appended:
                values_appended.append(attribute['value'])
                attributes_to_be_created.append(
                    ExpenseAttribute(
                        attribute_type=attribute_type,
                        display_name=attribute['display_name'],
                        value=attribute['value'],
                        source_id=attribute['source_id'],
                        detail=attribute['detail'] if 'detail' in attribute else None,
                        workspace_id=workspace_id,
                        active=attribute['active'] if 'active' in attribute else None
                    )
                )
            else:
                if update:
                    attributes_to_be_updated.append(
                        ExpenseAttribute(
                            id=primary_key_map[attribute['value']]['id'],
                            source_id=attribute['source_id'],
                            detail=attribute['detail'] if 'detail' in attribute else None,
                            active=attribute['active'] if 'active' in attribute else None
                        )
                    )
        if attributes_to_be_created:
            ExpenseAttribute.objects.bulk_create(attributes_to_be_created, batch_size=50)

        if attributes_to_be_updated:
            ExpenseAttribute.objects.bulk_update(
                attributes_to_be_updated, fields=['source_id', 'detail', 'active'], batch_size=50)

    @staticmethod
    def get_last_synced_at(attribute_type: str, workspace_id: int):
        """
        Get last synced at datetime
        :param attribute_type: Attribute type
        :param workspace_id: Workspace Id
        :return: last_synced_at datetime
        """
        return ExpenseAttribute.objects.filter(
            workspace_id=workspace_id,
            attribute_type=attribute_type
        ).order_by('-updated_at').first()


class DestinationAttribute(models.Model):
    """
    Destination Expense Attributes
    """
    id = models.AutoField(primary_key=True)
    attribute_type = models.CharField(max_length=255, help_text='Type of expense attribute')
    display_name = models.CharField(max_length=255, help_text='Display name of attribute')
    value = models.CharField(max_length=255, help_text='Value of expense attribute')
    destination_id = models.CharField(max_length=255, help_text='Destination ID')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    auto_created = models.BooleanField(default=False,
                                       help_text='Indicates whether the field is auto created by the integration')
    active = models.BooleanField(null=True, help_text='Indicates whether the fields is active or not')
    detail = JSONField(help_text='Detailed destination attributes payload', null=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'destination_attributes'
        unique_together = ('destination_id', 'attribute_type', 'workspace', 'display_name')

    @staticmethod
    def create_or_update_destination_attribute(attribute: Dict, workspace_id):
        """
        get or create destination attributes
        """
        destination_attribute, _ = DestinationAttribute.objects.update_or_create(
            attribute_type=attribute['attribute_type'],
            destination_id=attribute['destination_id'],
            workspace_id=workspace_id,
            defaults={
                'active': attribute['active'] if 'active' in attribute else None,
                'display_name': attribute['display_name'],
                'value': attribute['value'],
                'detail': attribute['detail'] if 'detail' in attribute else None
            }
        )
        return destination_attribute

    @staticmethod
    def bulk_create_or_update_destination_attributes(
            attributes: List[Dict], attribute_type: str, workspace_id: int, update: bool = False, display_name: str = None):
        """
        Create Destination Attributes in bulk
        :param update: Update Pre-existing records or not
        :param attribute_type: Attribute type
        :param attributes: attributes = [{
            'attribute_type': Type of attribute,
            'display_name': Display_name of attribute_field,
            'value': Value of attribute,
            'destination_id': Destination Id of the attribute,
            'detail': Extra Details of the attribute
        }]
        :param workspace_id: Workspace Id
        :return: created / updated attributes
        """
        attribute_destination_id_list = [attribute['destination_id'] for attribute in attributes]

        filters = {
            'destination_id__in': attribute_destination_id_list,
            'attribute_type': attribute_type,
            'workspace_id': workspace_id
        }
        if display_name:
            filters['display_name'] = display_name

        existing_attributes = DestinationAttribute.objects.filter(**filters)\
            .values('id', 'value', 'destination_id', 'detail', 'active')

        existing_attribute_destination_ids = []

        primary_key_map = {}

        for existing_attribute in existing_attributes:
            existing_attribute_destination_ids.append(existing_attribute['destination_id'])
            primary_key_map[existing_attribute['destination_id']] = {
                'id': existing_attribute['id'],
                'value': existing_attribute['value'],
                'detail': existing_attribute['detail'],
                'active' : existing_attribute['active']
            }

        attributes_to_be_created = []
        attributes_to_be_updated = []

        destination_ids_appended = []
        for attribute in attributes:
            if attribute['destination_id'] not in existing_attribute_destination_ids \
                    and attribute['destination_id'] not in destination_ids_appended:
                destination_ids_appended.append(attribute['destination_id'])
                attributes_to_be_created.append(
                    DestinationAttribute(
                        attribute_type=attribute_type,
                        display_name=attribute['display_name'],
                        value=attribute['value'],
                        destination_id=attribute['destination_id'],
                        detail=attribute['detail'] if 'detail' in attribute else None,
                        workspace_id=workspace_id,
                        active=attribute['active'] if 'active' in attribute else None
                    )
                )
            else:
                if update and(
                        (attribute['value'] != primary_key_map[attribute['destination_id']]['value'])
                        or
                        ('detail' in attribute and attribute['detail'] != primary_key_map[attribute['destination_id']]['detail'])
                        or
                        ('active' in attribute and attribute['active'] != primary_key_map[attribute['destination_id']]['active'])
                    ):
                    attributes_to_be_updated.append(
                        DestinationAttribute(
                            id=primary_key_map[attribute['destination_id']]['id'],
                            value=attribute['value'],
                            detail=attribute['detail'] if 'detail' in attribute else None,
                            active=attribute['active'] if 'active' in attribute else None,
                            updated_at=datetime.now()
                        )
                    )
        if attributes_to_be_created:
            DestinationAttribute.objects.bulk_create(attributes_to_be_created, batch_size=50)

        if attributes_to_be_updated:
            DestinationAttribute.objects.bulk_update(
                attributes_to_be_updated, fields=['detail', 'value', 'active', 'updated_at'], batch_size=50)


class ExpenseField(models.Model):
    """
    Expense Fields
    """

    id = models.AutoField(primary_key=True)
    attribute_type = models.CharField(max_length=255, help_text='Attribute Type')
    source_field_id = models.IntegerField(help_text='Field ID')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    is_enabled = models.BooleanField(default=False, help_text='Is the field Enabled')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'expense_fields'
        unique_together = ('attribute_type', 'workspace_id')


    @staticmethod
    def create_or_update_expense_fields(attributes: List[Dict], fields_included: List[str], workspace_id):
        """
        Update or Create Expense Fields
        """
        # Looping over Expense Field Values
        expense_fields = None
        for expense_field in attributes:
            if expense_field['field_name'] in fields_included or expense_field['type'] == 'DEPENDENT_SELECT':
                expense_fields, _ = ExpenseField.objects.update_or_create(
                    attribute_type=expense_field['field_name'].replace(' ', '_').upper(),
                    workspace_id=workspace_id,
                    defaults={
                        'source_field_id': expense_field['id'],
                        'is_enabled': expense_field['is_enabled'] if 'is_enabled' in expense_field else False
                    }
                )

        return expense_fields


class MappingSetting(models.Model):
    """
    Mapping Settings
    """
    id = models.AutoField(primary_key=True)
    source_field = models.CharField(max_length=255, help_text='Source mapping field')
    destination_field = models.CharField(max_length=255, help_text='Destination mapping field')
    import_to_fyle = models.BooleanField(default=False, help_text='Import to Fyle or not')
    is_custom = models.BooleanField(default=False, help_text='Custom Field or not')
    source_placeholder = models.TextField(help_text='placeholder of source field', null=True)
    expense_field = models.ForeignKey(
        ExpenseField, on_delete=models.PROTECT, help_text='Reference to Expense Field model',
        related_name='expense_fields', null=True
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model',
        related_name='mapping_settings'
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('source_field', 'destination_field', 'workspace')
        db_table = 'mapping_settings'

    @staticmethod
    def bulk_upsert_mapping_setting(settings: List[Dict], workspace_id: int):
        """
        Bulk update or create mapping setting
        """
        validate_mapping_settings(settings)
        mapping_settings = []

        with transaction.atomic():
            for setting in settings:

                mapping_setting, _ = MappingSetting.objects.update_or_create(
                    source_field=setting['source_field'],
                    workspace_id=workspace_id,
                    destination_field=setting['destination_field'],
                    expense_field_id=setting['parent_field'] if 'parent_field' in setting else None,
                    defaults={
                        'import_to_fyle': setting['import_to_fyle'] if 'import_to_fyle' in setting else False,
                        'is_custom': setting['is_custom'] if 'is_custom' in setting else False
                    }
                )
                mapping_settings.append(mapping_setting)

            return mapping_settings


class Mapping(models.Model):
    """
    Mappings
    """
    id = models.AutoField(primary_key=True)
    source_type = models.CharField(max_length=255, help_text='Fyle Enum')
    destination_type = models.CharField(max_length=255, help_text='Destination Enum')
    source = models.ForeignKey(ExpenseAttribute, on_delete=models.PROTECT, related_name='mapping')
    destination = models.ForeignKey(DestinationAttribute, on_delete=models.PROTECT, related_name='mapping')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        unique_together = ('source_type', 'source', 'destination_type', 'workspace')
        db_table = 'mappings'

    @staticmethod
    def create_or_update_mapping(source_type: str, destination_type: str,
                                 source_value: str, destination_value: str, destination_id: str, workspace_id: int):
        """
        Bulk update or create mappings
        source_type = 'Type of Source attribute, eg. CATEGORY',
        destination_type = 'Type of Destination attribute, eg. ACCOUNT',
        source_value = 'Source value to be mapped, eg. category name',
        destination_value = 'Destination value to be mapped, eg. account name'
        workspace_id = Unique Workspace id
        """
        settings = MappingSetting.objects.filter(source_field=source_type, destination_field=destination_type,
                                                 workspace_id=workspace_id).first()

        assert_valid(
            settings is not None and settings != [],
            'Settings for Destination  {0} / Source {1} not found'.format(destination_type, source_type)
        )

        mapping, _ = Mapping.objects.update_or_create(
            source_type=source_type,
            source=ExpenseAttribute.objects.filter(
                attribute_type=source_type, value__iexact=source_value, workspace_id=workspace_id
            ).first() if source_value else None,
            destination_type=destination_type,
            workspace=Workspace.objects.get(pk=workspace_id),
            defaults={
                'destination': DestinationAttribute.objects.get(
                    attribute_type=destination_type,
                    value=destination_value,
                    destination_id=destination_id,
                    workspace_id=workspace_id
                )
            }
        )
        return mapping

    @staticmethod
    def bulk_create_mappings(destination_attributes: List[DestinationAttribute], source_type: str,
                             destination_type: str, workspace_id: int, set_auto_mapped_flag: bool = True):
        """
        Bulk create mappings
        :param set_auto_mapped_flag: set auto mapped to expense attributes
        :param destination_type: Destination Type
        :param source_type: Source Type
        :param destination_attributes: Destination Attributes List
        :param workspace_id: workspace_id
        :return: mappings list
        """
        attribute_value_list = []

        for destination_attribute in destination_attributes:
            attribute_value_list.append(destination_attribute.value)

        source_attributes: List[ExpenseAttribute] = ExpenseAttribute.objects.filter(
            value__in=attribute_value_list, workspace_id=workspace_id,
            attribute_type=source_type, mapping__source_id__isnull=True).all()

        source_value_id_map = {}

        for source_attribute in source_attributes:
            source_value_id_map[source_attribute.value.lower()] = source_attribute.id

        mapping_batch = []

        for destination_attribute in destination_attributes:
            if destination_attribute.value.lower() in source_value_id_map:
                mapping_batch.append(
                    Mapping(
                        source_type=source_type,
                        destination_type=destination_type,
                        source_id=source_value_id_map[destination_attribute.value.lower()],
                        destination_id=destination_attribute.id,
                        workspace_id=workspace_id
                    )
                )

        return create_mappings_and_update_flag(mapping_batch, set_auto_mapped_flag)

    @staticmethod
    def auto_map_employees(destination_type: str, employee_mapping_preference: str, workspace_id: int):
        """
        Auto map employees
        :param destination_type: Destination Type of mappings
        :param employee_mapping_preference: Employee Mapping Preference
        :param workspace_id: Workspace ID
        """
        # Filtering only not mapped destination attributes
        employee_destination_attributes = DestinationAttribute.objects.filter(
            attribute_type=destination_type, workspace_id=workspace_id).all()

        destination_id_value_map = {}
        for destination_employee in employee_destination_attributes:
            value_to_be_appended = None
            if employee_mapping_preference == 'EMAIL' and destination_employee.detail \
                    and destination_employee.detail['email']:
                value_to_be_appended = destination_employee.detail['email'].replace('*', '')
            elif employee_mapping_preference in ['NAME', 'EMPLOYEE_CODE']:
                value_to_be_appended = destination_employee.value.replace('*', '')

            if value_to_be_appended:
                destination_id_value_map[value_to_be_appended.lower()] = destination_employee.id

        employee_source_attributes_count = ExpenseAttribute.objects.filter(
            attribute_type='EMPLOYEE', workspace_id=workspace_id, auto_mapped=False
        ).count()
        page_size = 200
        employee_source_attributes = []

        for offset in range(0, employee_source_attributes_count, page_size):
            limit = offset + page_size
            paginated_employee_source_attributes = ExpenseAttribute.objects.filter(
                attribute_type='EMPLOYEE', workspace_id=workspace_id, auto_mapped=False
            )[offset:limit]
            employee_source_attributes.extend(paginated_employee_source_attributes)

        mapping_batch = construct_mapping_payload(
            employee_source_attributes, employee_mapping_preference,
            destination_id_value_map, destination_type, workspace_id
        )

        create_mappings_and_update_flag(mapping_batch)

    @staticmethod
    def auto_map_ccc_employees(destination_type: str, default_ccc_account_id: str, workspace_id: int):
        """
        Auto map ccc employees
        :param destination_type: Destination Type of mappings
        :param default_ccc_account_id: Default CCC Account
        :param workspace_id: Workspace ID
        """
        employee_source_attributes = ExpenseAttribute.objects.filter(
            attribute_type='EMPLOYEE', workspace_id=workspace_id
        ).all()

        default_destination_attribute = DestinationAttribute.objects.filter(
            destination_id=default_ccc_account_id, workspace_id=workspace_id, attribute_type=destination_type
        ).first()

        existing_source_ids = get_existing_source_ids(destination_type, workspace_id)

        mapping_batch = []
        for source_employee in employee_source_attributes:
            # Ignoring already present mappings
            if source_employee.id not in existing_source_ids:
                mapping_batch.append(
                    Mapping(
                        source_type='EMPLOYEE',
                        destination_type=destination_type,
                        source_id=source_employee.id,
                        destination_id=default_destination_attribute.id,
                        workspace_id=workspace_id
                    )
                )

        Mapping.objects.bulk_create(mapping_batch, batch_size=50)


class EmployeeMapping(models.Model):
    """
    Employee Mappings
    """
    id = models.AutoField(primary_key=True)
    source_employee = models.ForeignKey(
        ExpenseAttribute, on_delete=models.PROTECT, related_name='employeemapping')
    destination_employee = models.ForeignKey(
        DestinationAttribute, on_delete=models.PROTECT, null=True, related_name='destination_employee')
    destination_vendor = models.ForeignKey(
        DestinationAttribute, on_delete=models.PROTECT, null=True, related_name='destination_vendor')
    destination_card_account = models.ForeignKey(
        DestinationAttribute, on_delete=models.PROTECT, null=True, related_name='destination_card_account')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'employee_mappings'

    @staticmethod
    def create_or_update_employee_mapping(
            source_employee_id: int, workspace: Workspace,
            destination_employee_id: int = None, destination_vendor_id: int = None,
            destination_card_account_id: int = None):
        """
        Create single instance of employee mappings
        :param source_employee_id: employee expense attribute id
        :param workspace: workspace instance
        :param destination_employee_id: employee destination attribute id
        :param destination_vendor_id: vendor destination attribute id
        :param destination_card_account_id: card destination attribute id
        :return:
        """
        employee_mapping, _ = EmployeeMapping.objects.update_or_create(
            source_employee_id=source_employee_id,
            workspace=workspace,
            defaults={
                'destination_employee_id': destination_employee_id,
                'destination_vendor_id': destination_vendor_id,
                'destination_card_account_id': destination_card_account_id
            }
        )

        return employee_mapping


class CategoryMapping(models.Model):
    """
    Category Mappings
    """
    id = models.AutoField(primary_key=True)
    source_category = models.ForeignKey(ExpenseAttribute, on_delete=models.PROTECT, related_name='categorymapping')
    destination_account = models.ForeignKey(
        DestinationAttribute, on_delete=models.PROTECT, null=True, related_name='destination_account')
    destination_expense_head = models.ForeignKey(
        DestinationAttribute, on_delete=models.PROTECT, null=True, related_name='destination_expense_head')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, help_text='Reference to Workspace model')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Created at datetime')
    updated_at = models.DateTimeField(auto_now=True, help_text='Updated at datetime')

    class Meta:
        db_table = 'category_mappings'

    @staticmethod
    def create_or_update_category_mapping(
            source_category_id: int, workspace: Workspace,
            destination_account_id: int = None, destination_expense_head_id: int = None):
        """
        Create single instance of category mappings
        :param source_category_id: category expense attribute id
        :param workspace: workspace instance
        :param destination_account_id: category destination attribute id
        :param destination_expense_head_id: expense head destination attribute id
        :return:
        """
        category_mapping, _ = CategoryMapping.objects.update_or_create(
            source_category_id=source_category_id,
            workspace=workspace,
            defaults={
                'destination_account_id': destination_account_id,
                'destination_expense_head_id': destination_expense_head_id
            }
        )

        return category_mapping

    @staticmethod
    def bulk_create_mappings(destination_attributes: List[DestinationAttribute],
                             destination_type: str, workspace_id: int, set_auto_mapped_flag: bool = True):
        """
        Create the bulk mapping
        :param destination_attributes: Destination Attributes List with category mapping as null
        """
        attribute_value_list = []

        for destination_attribute in destination_attributes:
            attribute_value_list.append(destination_attribute.value)

        # Filtering unmapped Expense Attributes
        source_attributes = ExpenseAttribute.objects.filter(
            workspace_id=workspace_id,
            attribute_type='CATEGORY',
            value__in=attribute_value_list,
            categorymapping__source_category__isnull=True
        ).values('id', 'value')

        source_attributes_id_map = {source_attribute['value'].lower(): source_attribute['id'] \
            for source_attribute in source_attributes}

        mapping_creation_batch = []

        for destination_attribute in destination_attributes:
            if destination_attribute.value.lower() in source_attributes_id_map:
                destination = {}
                if destination_type in ('EXPENSE_TYPE', 'EXPENSE_CATEGORY'):
                    destination['destination_expense_head_id'] = destination_attribute.id
                elif destination_type == 'ACCOUNT':
                    destination['destination_account_id'] = destination_attribute.id

                mapping_creation_batch.append(
                    CategoryMapping(
                        source_category_id=source_attributes_id_map[destination_attribute.value.lower()],
                        workspace_id=workspace_id,
                        **destination
                    )
                )

        return create_mappings_and_update_flag(mapping_creation_batch, set_auto_mapped_flag, model_type=CategoryMapping)

    @staticmethod
    def bulk_create_ccc_category_mappings(workspace_id: int):
        """
        Create Category Mappings for CCC Expenses
        :param workspace_id: Workspace ID
        """
        category_mappings = CategoryMapping.objects.filter(
            workspace_id=workspace_id,
            destination_account__isnull=True
        ).all()

        destination_account_internal_ids = []

        for category_mapping in category_mappings:
            if category_mapping.destination_expense_head.detail and \
                'gl_account_no' in category_mapping.destination_expense_head.detail and \
                    category_mapping.destination_expense_head.detail['gl_account_no']:
                destination_account_internal_ids.append(category_mapping.destination_expense_head.detail['gl_account_no'])

            elif category_mapping.destination_expense_head.detail and \
                'account_internal_id' in category_mapping.destination_expense_head.detail and \
                    category_mapping.destination_expense_head.detail['account_internal_id']:
                destination_account_internal_ids.append(category_mapping.destination_expense_head.detail['account_internal_id'])

        # Retreiving accounts for creating ccc mapping
        destination_attributes = DestinationAttribute.objects.filter(
            workspace_id=workspace_id,
            attribute_type='ACCOUNT',
            destination_id__in=destination_account_internal_ids
        ).values('id', 'destination_id')

        destination_id_pk_map = {}
        for attribute in destination_attributes:
            destination_id_pk_map[attribute['destination_id'].lower()] = attribute['id']

        mapping_updation_batch = []

        for category_mapping in category_mappings:
            ccc_account_id = None

            if category_mapping.destination_expense_head.detail and \
                'gl_account_no' in category_mapping.destination_expense_head.detail and\
                category_mapping.destination_expense_head.detail['gl_account_no'].lower() in destination_id_pk_map:
                ccc_account_id = destination_id_pk_map[category_mapping.destination_expense_head.detail['gl_account_no'].lower()]

            elif category_mapping.destination_expense_head.detail and \
                'account_internal_id' in category_mapping.destination_expense_head.detail and \
                category_mapping.destination_expense_head.detail['account_internal_id'].lower() in destination_id_pk_map:
                ccc_account_id = destination_id_pk_map[category_mapping.destination_expense_head.detail['account_internal_id'].lower()]

            mapping_updation_batch.append(
                CategoryMapping(
                    id=category_mapping.id,
                    source_category_id=category_mapping.source_category.id,
                    destination_account_id=ccc_account_id
                )
            )

        if mapping_updation_batch:
            CategoryMapping.objects.bulk_update(
                mapping_updation_batch, fields=['destination_account'], batch_size=50
            )
