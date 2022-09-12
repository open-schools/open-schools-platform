from rest_framework import serializers

from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.employees.serializers import 


class CreateOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", 'inn')
        extra_kwargs = {"name": {'required': True}}


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "inn")
        read_only_fields = fields
