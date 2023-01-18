from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from rest_framework import serializers
from fyle_accounting_mappings.models import MappingSetting

from apps.workspaces.models import WorkspaceGeneralSettings
from apps.mappings.models import GeneralMapping
from apps.fyle.models import ExpenseGroupSettings
from .triggers import ExportSettingsTrigger


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
        fields = [
            'reimbursable_expenses_object',
            'corporate_credit_card_expenses_object',
            'auto_map_employees',
            'is_simplify_report_closure_enabled'
        ]
        read_only_fields = ['is_simplify_report_closure_enabled']


class GeneralMappingsSerializer(serializers.ModelSerializer):
    bank_account = ReadWriteSerializerMethodField()

    class Meta:
        model = GeneralMapping
        fields = ['bank_account']

    def get_bank_account(self, instance):
        return {
            'id': instance.bank_account_id,
            'name': instance.bank_account_name
        }

class ExpenseGroupSettingsSerializer(serializers.ModelSerializer):
    reimbursable_expense_group_fields = serializers.ListField(allow_null=True, required=False)
    reimbursable_export_date_type = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    reimbursable_expense_state = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    corporate_credit_card_expense_group_fields = serializers.ListField(allow_null=True, required=False)
    ccc_export_date_type = serializers.CharField(allow_null=True, allow_blank=True, required=False) 
    ccc_expense_state = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = ExpenseGroupSettings
        fields = [
            'reimbursable_expense_group_fields',
            'reimbursable_export_date_type',
            'reimbursable_expense_state',
            'corporate_credit_card_expense_group_fields',
            'ccc_export_date_type',
            'ccc_expense_state'
        ]


class ExportSettingsSerializer(serializers.ModelSerializer):
    workspace_general_settings = WorkspaceGeneralSettingsSerializer()
    expense_group_settings = ExpenseGroupSettingsSerializer()
    general_mappings = GeneralMappingsSerializer()
    workspace_id = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'workspace_general_settings',
            'expense_group_settings',
            'general_mappings',
            'workspace_id'
        ]
        read_only_fields = ['workspace_id']

    def get_workspace_id(self, instance):
        return instance.id
    
    def update(self, instance, validated):
        workspace_general_settings = validated.pop('workspace_general_settings')
        expense_group_settings = validated.pop('expense_group_settings')
        general_mappings = validated.pop('general_mappings')
        workspace_id = instance.id

        workspace_general_settings_instance = WorkspaceGeneralSettings.objects.filter(workspace_id=workspace_id).first()

        map_merchant_to_contact = True

        if workspace_general_settings_instance:
            map_merchant_to_contact = workspace_general_settings_instance.map_merchant_to_contact

        workspace_general_settings_instance, _ = WorkspaceGeneralSettings.objects.update_or_create(
            workspace_id=workspace_id,
            defaults={
                'auto_map_employees': workspace_general_settings['auto_map_employees'],
                'reimbursable_expenses_object': workspace_general_settings['reimbursable_expenses_object'], 
                'corporate_credit_card_expenses_object': workspace_general_settings['corporate_credit_card_expenses_object'],
                'map_merchant_to_contact': map_merchant_to_contact
            }
        )

        expense_group_settings['import_card_credits'] = False

        if workspace_general_settings['corporate_credit_card_expenses_object'] == 'BANK TRANSACTION':
            MappingSetting.objects.update_or_create(
                destination_field='BANK_ACCOUNT',
                workspace_id=instance.id,
                defaults={
                    'source_field': 'CORPORATE_CARD',
                    'import_to_fyle': False,
                    'is_custom': False
                }
            )
            expense_group_settings['import_card_credits'] = True

        ExportSettingsTrigger.run_workspace_general_settings_triggers(workspace_general_settings_instance)

        expense_group_settings_instance = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
        expense_group_settings['expense_state'] = expense_group_settings_instance.expense_state
        expense_group_settings['reimbursable_expense_group_fields'] = expense_group_settings_instance.reimbursable_expense_group_fields
        expense_group_settings['corporate_credit_card_expense_group_fields'] = expense_group_settings_instance.corporate_credit_card_expense_group_fields
        expense_group_settings['ccc_export_date_type'] = expense_group_settings_instance.ccc_export_date_type
        expense_group_settings['reimbursable_expense_state'] = expense_group_settings['reimbursable_expense_state']
        expense_group_settings['ccc_expense_state'] = expense_group_settings['ccc_expense_state']

        if 'expense_state' in expense_group_settings and not expense_group_settings['expense_state']:
            expense_group_settings['expense_state'] = 'PAYMENT_PROCESSING'

        if not expense_group_settings['reimbursable_export_date_type']:
            expense_group_settings['reimbursable_export_date_type'] = 'current_date'

        if not expense_group_settings['ccc_export_date_type']:
            expense_group_settings['ccc_export_date_type'] = 'spent_at'

        ExpenseGroupSettings.update_expense_group_settings(expense_group_settings, workspace_id=workspace_id)
        GeneralMapping.objects.update_or_create(
            workspace=instance,
            defaults={
                'bank_account_name': general_mappings.get('bank_account').get('name'),
                'bank_account_id': general_mappings.get('bank_account').get('id')
            }
        )

        if instance.onboarding_state == 'EXPORT_SETTINGS':
            instance.onboarding_state = 'IMPORT_SETTINGS'
            instance.save()

        return instance
    
    def validate(self, data):
        if not data.get('workspace_general_settings'):
            raise serializers.ValidationError('Workspace general settings are required')

        if not data.get('expense_group_settings'):
            raise serializers.ValidationError('Expense group settings are required')

        if not data.get('general_mappings'):
            raise serializers.ValidationError('General mappings are required')

        if data['workspace_general_settings']['corporate_credit_card_expenses_object'] == 'BANK TRANSACTION' \
            and not data['general_mappings']['bank_account']['id']:
            raise serializers.ValidationError('Bank account id is required')

        if data['workspace_general_settings']['corporate_credit_card_expenses_object'] == 'BANK TRANSACTION' \
            and not data['general_mappings']['bank_account']['name']:
            raise serializers.ValidationError('Bank account name is required')

        if data.get('workspace_general_settings').get('auto_map_employees') and \
            data.get('workspace_general_settings').get('auto_map_employees') not in ['EMAIL', 'NAME', 'EMPLOYEE_CODE']:
            raise serializers.ValidationError('auto_map_employees can have only EMAIL / NAME / EMPLOYEE_CODE')

        return data
