from rest_framework import serializers

from open_schools_platform.organization_management.organizations.models import Organization


class CreateOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", "inn")


class RetrieveOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("pk", "name", "inn")
