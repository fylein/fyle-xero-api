from rest_framework import serializers

from .models import TenantMapping, GeneralMapping


class TenantMappingSerializer(serializers.ModelSerializer):
    """
    Tenant mappings group serializer
    """
    class Meta:
        model = TenantMapping
        fields = '__all__'


class GeneralMappingSerializer(serializers.ModelSerializer):
    """
    General mappings group serializer
    """
    class Meta:
        model = GeneralMapping
        fields = '__all__'
