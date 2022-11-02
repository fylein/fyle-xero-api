from rest_framework import serializers

from fyle_accounting_mappings.models import DestinationAttribute

from apps.xero.models import BankTransaction, BankTransactionLineItem, Bill, BillLineItem


class XeroFieldSerializer(serializers.ModelSerializer):
    """
    Xero Fields Serializer
    """
    class Meta:
        model = DestinationAttribute
        fields = ['attribute_type', 'display_name']


class BankTransactionLineitemsSerializer(serializers.ModelSerializer):
    """
    Xero Bank Transaction Lineitems serializer
    """
    class Meta:
        model = BankTransactionLineItem
        fields = '__all__'


class BillTransactionLineitemsSerializer(serializers.ModelSerializer):
    """
    Xero Bill Lineitems serializer
    """
    class Meta:
        model = BillLineItem
        fields = '__all__'
