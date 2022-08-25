from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.organizations.models import Organization


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


class OrganizationInviteSerializer(serializers.Serializer):
    phone = PhoneNumberField(max_length=17, required=True)
    name = serializers.CharField(max_length=255, required=True)
    position = serializers.CharField(max_length=255, required=True)


class OrganizationInviteUpdateSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    name = serializers.CharField(max_length=255, required=False, default=None)
    position = serializers.CharField(max_length=255, required=False, default=None)
