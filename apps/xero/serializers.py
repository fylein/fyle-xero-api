from rest_framework import serializers

from fyle_accounting_mappings.models import DestinationAttribute

from apps.xero.models import BankTransaction, BankTransactionLineItem


class XeroFieldSerializer(serializers.ModelSerializer):
    """
    Xero Fields Serializer
    """
    class Meta:
        model = DestinationAttribute
        fields = ['attribute_type', 'display_name']


class BankTransactionSerializer(serializers.ModelSerializer):
    """
    Xero Bank Transaction serializer
    """
    class Meta:
        model = BankTransaction
        fields = '__all__'


class BankTransactionLineitemsSerializer(serializers.ModelSerializer):
    """
    Xero Bank Transaction Lineitems serializer
    """
    class Meta:
        model = BankTransactionLineItem
        fields = '__all__'
