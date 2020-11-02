from rest_framework import serializers

from fyle_accounting_mappings.models import DestinationAttribute


class XeroFieldSerializer(serializers.ModelSerializer):
    """
    Xero Fields Serializer
    """
    class Meta:
        model = DestinationAttribute
        fields = ['attribute_type', 'display_name']
