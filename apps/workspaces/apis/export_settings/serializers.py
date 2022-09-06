from statistics import mode

from attr import fields
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from rest_framework import serializers

from apps.workspaces.models import WorkspaceGeneralSettings
from apps.mappings.models import GeneralMapping
from apps.fyle.models import ExpenseGroupSettings

class ReadWriteSerializerMethodField(serializers.SerializerMethodField):
    """
    Serializer Method Field to Read and Write from values
    Inherits serializers.SerializerMethodField
    """

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return {
            self.field_name: data
        }

class WorkspaceGeneralSettingsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WorkspaceGeneralSettings
        fields = ['reimbursable_expenses_object', 'corporate_credit_card_expenses_object', 'auto_map_employees']

class GeneralMappingsSerializer(serializers.ModelSerializer):
    bank_account = ReadWriteSerializerMethodField()
    payment_account = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = ['bank_account','payment_account']

    def get_bank_account(self, instance):
        return {
            'id': instance.bank_account_id,
            'name': instance.bank_account_name
        }

    def get_payment_account(self, instance):
        return {
            'id': instance.payment_account_id,
            'name': instance.payment_account_name
        }

class ExpenseGroupSettingsSerializer(serializers.ModelSerializer):
    reimbursable_expense_group_fields = serializers.ListField(allow_null=True, required=False) #remove this
    reimbursable_export_date_type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    reimbursable_expense_state = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    corporate_credit_card_expense_group_fields = serializers.ListField(allow_null=True, required=False) #remove this
    ccc_export_date_type = serializers.CharField(allow_null=True, allow_blank=True, required=False) #remove this 
    ccc_expense_state = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = ExpenseGroupSettings
        fields = [ #remove here as well .
            'reimbursable_expense_group_fields',
            'reimbursable_export_date_type',
            'reimbursable_expense_state',
            'corporate_credit_card_expense_group_fields',
            'ccc_export_date_type',
            'ccc_expense_state'
        ]





class ExportSettingsSerializer(serializers.ModelSerializer) :
    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    expense_group_settings = ExpenseGroupSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = {
            'workspace_general_settings',
            'expense_group_settings',
            'general_mappings',
            'workspace_id'
        }
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id
    
    def update(self, instance, validated):
        workspace_general_settings = validated.pop('workspace_general_settings')
        expense_group_settings = validated.pop('expense_group_settings')
        general_mappings = validated.pop('general_mappings')
        workspace_id = instance.id

        workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

        workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults={
                'auto_map_employees': workspace_general_settings['auto_map_employees'],
                'reimbursable_expenses_object': workspace_general_settings['reimbursable_expenses_object'], 
                'corporate_credit_card_expenses_object': workspace_general_settings['corporate_credit_card_expenses_object']
            }
        )

        return instance
    
    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if not data.get('expense_group_settings'):
            raise serializers.ValidationError('Expense group settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')
        return data