"""
Mapping Serializers
"""
from rest_framework import serializers
from django.db.models.query import Q
from .models import ExpenseAttribute, DestinationAttribute, Mapping, MappingSetting, EmployeeMapping, \
    CategoryMapping, ExpenseField


class ExpenseAttributeSerializer(serializers.ModelSerializer):
    """
    Expense Attribute serializer
    """
    id = serializers.IntegerField()

    class Meta:
        model = ExpenseAttribute
        fields = '__all__'
        read_only_fields = (
            'value', 'attribute_type', 'source_id', 'workspace', 'detail',
            'auto_mapped', 'auto_created', 'active', 'display_name'
        )


class DestinationAttributeSerializer(serializers.ModelSerializer):
    """
    Destination Attribute serializer
    """
    id = serializers.IntegerField(allow_null=True)

    class Meta:
        model = DestinationAttribute
        fields = '__all__'
        read_only_fields = (
            'value', 'attribute_type', 'destination_id', 'workspace', 'detail',
            'auto_created', 'active', 'display_name'
        )


class ExpenseFieldSerializer(serializers.ModelSerializer):
    """
    Expense Field Serializer
    """

    class Meta:
        model = ExpenseField
        fields = '__all__'


class MappingSettingSerializer(serializers.ModelSerializer):
    """
    Mapping Setting serializer
    """

    class Meta:
        model = MappingSetting
        fields = '__all__'


class MappingSerializer(serializers.ModelSerializer):
    """
    Mapping serializer
    """
    source = ExpenseAttributeSerializer()
    destination = DestinationAttributeSerializer()

    class Meta:
        model = Mapping
        fields = '__all__'


class EmployeeMappingSerializer(serializers.ModelSerializer):
    """
    Mapping serializer
    """
    source_employee = ExpenseAttributeSerializer(required=True)
    destination_employee = DestinationAttributeSerializer(allow_null=True)
    destination_vendor = DestinationAttributeSerializer(allow_null=True)
    destination_card_account = DestinationAttributeSerializer(allow_null=True)

    class Meta:
        model = EmployeeMapping
        fields = '__all__'

    def validate_source_employee(self, source_employee):
        attribute = ExpenseAttribute.objects.filter(
            id=source_employee['id'],
            workspace_id=self.initial_data['workspace'],
            attribute_type='EMPLOYEE'
        ).first()

        if not attribute:
            raise serializers.ValidationError('No attribute found with this attribute id')

        attribute.auto_mapped = False
        attribute.save()

        return source_employee

    def validate_destination_employee(self, destination_employee):
        if destination_employee and 'id' in destination_employee and destination_employee['id']:
            attribute = DestinationAttribute.objects.filter(
                id=destination_employee['id'],
                workspace_id=self.initial_data['workspace'],
                attribute_type='EMPLOYEE'
            ).first()

            if not attribute:
                raise serializers.ValidationError('No attribute found with this attribute id')
        return destination_employee

    def validate_destination_vendor(self, destination_vendor):
        if destination_vendor and 'id' in destination_vendor and destination_vendor['id']:
            attribute = DestinationAttribute.objects.filter(
                id=destination_vendor['id'],
                workspace_id=self.initial_data['workspace'],
                attribute_type='VENDOR'
            ).first()

            if not attribute:
                raise serializers.ValidationError('No attribute found with this attribute id')
        return destination_vendor

    def validate_destination_card_account(self, destination_card_account):
        if destination_card_account and 'id' in destination_card_account and destination_card_account['id']:
            attribute = DestinationAttribute.objects.filter(
                Q(attribute_type='CREDIT_CARD_ACCOUNT') | Q(attribute_type='CHARGE_CARD_NUMBER'),
                id=destination_card_account['id'],
                workspace_id=self.initial_data['workspace']
            ).first()

            if not attribute:
                raise serializers.ValidationError('No attribute found with this attribute id')
        return destination_card_account

    def create(self, validated_data):
        """
        Validated Data to be created
        :param validated_data:
        :return: Created Entry
        """
        employee_mapping = EmployeeMapping.create_or_update_employee_mapping(
            source_employee_id=validated_data['source_employee']['id'],
            workspace=validated_data['workspace'],
            destination_employee_id=validated_data['destination_employee']['id'],
            destination_vendor_id=validated_data['destination_vendor']['id'],
            destination_card_account_id=validated_data['destination_card_account']['id']
        )

        return employee_mapping


class CategoryMappingSerializer(serializers.ModelSerializer):
    """
    Mapping serializer
    """
    source_category = ExpenseAttributeSerializer(required=True)
    destination_account = DestinationAttributeSerializer(allow_null=True)
    destination_expense_head = DestinationAttributeSerializer(allow_null=True)

    class Meta:
        model = CategoryMapping
        fields = '__all__'

    def validate_source_category(self, source_category):
        attribute = ExpenseAttribute.objects.filter(
            id=source_category['id'],
            workspace_id=self.initial_data['workspace'],
            attribute_type='CATEGORY'
        ).first()

        if not attribute:
            raise serializers.ValidationError('No attribute found with this attribute id')

        attribute.auto_mapped = False
        attribute.save()

        return source_category

    def validate_destination_account(self, destination_account):
        if destination_account and 'id' in destination_account and destination_account['id']:
            attribute = DestinationAttribute.objects.filter(
                id=destination_account['id'],
                workspace_id=self.initial_data['workspace'],
                attribute_type='ACCOUNT'
            ).first()

            if not attribute:
                raise serializers.ValidationError('No attribute found with this attribute id')
        return destination_account

    def validate_destination_expense_head(self, destination_expense_head):
        if destination_expense_head and 'id' in destination_expense_head and destination_expense_head['id']:
            attribute = DestinationAttribute.objects.filter(
                Q(attribute_type='EXPENSE_CATEGORY') | Q(attribute_type='EXPENSE_TYPE'),
                id=destination_expense_head['id'],
                workspace_id=self.initial_data['workspace']
            ).first()

            if not attribute:
                raise serializers.ValidationError('No attribute found with this attribute id')
        return destination_expense_head

    def create(self, validated_data):
        """
        Validated Data to be created
        :param validated_data:
        :return: Created Entry
        """
        category_mapping = CategoryMapping.create_or_update_category_mapping(
            source_category_id=validated_data['source_category']['id'],
            workspace=validated_data['workspace'],
            destination_expense_head_id=validated_data['destination_expense_head']['id'],
            destination_account_id=validated_data['destination_account']['id']
        )

        return category_mapping


class MappingFilteredListSerializer(serializers.ListSerializer):
    """
    Serializer to filter the active system, which is a boolen field in
    System Model. The value argument to to_representation() method is
    the model instance
    """

    def to_representation(self, data):
        params = self.context.get('request').query_params
        destination_type = params.get('destination_type')
        data = data.filter(destination_type=destination_type)
        return super(MappingFilteredListSerializer, self).to_representation(data)


class MappingSerializerV2(serializers.ModelSerializer):
    """
    Mapping serializer
    """
    destination = DestinationAttributeSerializer()

    class Meta:
        model = Mapping
        list_serializer_class = MappingFilteredListSerializer
        fields = ('destination', 'source_type', 'destination_type', 'created_at', 'updated_at')


class ExpenseAttributeMappingSerializer(serializers.ModelSerializer):
    """
    Mapping serializer
    """
    mapping = MappingSerializerV2(many=True)

    class Meta:
        model = ExpenseAttribute
        fields = '__all__'


class EmployeeMappingFilteredListSerializer(serializers.ListSerializer):
    """
    Serializer to filter the active system, which is a boolen field in
    System Model. The value argument to to_representation() method is
    the model instance
    """

    def to_representation(self, data):
        return super(EmployeeMappingFilteredListSerializer, self).to_representation(data)


class CategoryMappingFilteredListSerializer(serializers.ListSerializer):
    """
    Serializer to filter the active system, which is a boolen field in
    System Model. The value argument to to_representation() method is
    the model instance
    """

    def to_representation(self, data):
        return super(CategoryMappingFilteredListSerializer, self).to_representation(data)


class EmployeeMappingSerializerV2(serializers.ModelSerializer):
    """
    Employee Mapping V2 serializer
    """
    source_employee = ExpenseAttributeSerializer(required=True)
    destination_employee = DestinationAttributeSerializer(allow_null=True)
    destination_vendor = DestinationAttributeSerializer(allow_null=True)
    destination_card_account = DestinationAttributeSerializer(allow_null=True)

    class Meta:
        model = EmployeeMapping
        list_serializer_class = EmployeeMappingFilteredListSerializer
        fields = (
            'source_employee', 'destination_employee', 'destination_vendor', 'destination_card_account', 'created_at', 'updated_at'
        )


class EmployeeAttributeMappingSerializer(serializers.ModelSerializer):
    """
    Employee Attributes Mapping serializer
    """
    employeemapping = EmployeeMappingSerializerV2(many=True)

    class Meta:
        model = ExpenseAttribute
        fields = '__all__'


class CategoryMappingSerializerV2(serializers.ModelSerializer):
    """
    Category Mapping V2 serializer
    """
    source_category = ExpenseAttributeSerializer(required=True)
    destination_account = DestinationAttributeSerializer(allow_null=True)
    destination_expense_head = DestinationAttributeSerializer(allow_null=True)

    class Meta:
        model = CategoryMapping
        list_serializer_class = CategoryMappingFilteredListSerializer
        fields = ('source_category', 'destination_account', 'destination_expense_head', 'created_at', 'updated_at')


class CategoryAttributeMappingSerializer(serializers.ModelSerializer):
    """
    Employee Attributes Mapping serializer
    """
    categorymapping = CategoryMappingSerializerV2(many=True)

    class Meta:
        model = ExpenseAttribute
        fields = '__all__'


class FyleFieldsSerializer(serializers.Serializer):
    """
    Fyle Fields Serializer
    """

    attribute_type = serializers.CharField()
    display_name = serializers.CharField()
    is_dependant = serializers.BooleanField()

    def format_fyle_fields(self, workspace_id):
        """
        Get Fyle Fields
        """

        attribute_types = [
            'EMPLOYEE', 'CATEGORY', 'PROJECT', 'COST_CENTER',
            'TAX_GROUP', 'CORPORATE_CARD', 'MERCHANT'
        ]

        attributes = ExpenseAttribute.objects.filter(
            ~Q(attribute_type__in=attribute_types),
            workspace_id=workspace_id
        ).values('attribute_type', 'display_name', 'detail__is_dependent').distinct()

        attributes_list = [
            {'attribute_type': 'COST_CENTER', 'display_name': 'Cost Center', 'is_dependant': False},
            {'attribute_type': 'PROJECT', 'display_name': 'Project', 'is_dependant': False}
        ]

        for attr in attributes:
            attributes_list.append({
                'attribute_type': attr['attribute_type'],
                'display_name': attr['display_name'],
                'is_dependant': attr['detail__is_dependent']
            })

        return attributes_list
