from rest_framework import serializers

from .models import TenantMapping


class TenantMappingSerializer(serializers.ModelSerializer):
    """
    Tenant mappings group serializer
    """
    class Meta:
        model = TenantMapping
        fields = '__all__'
