import uuid

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.circles.serializers import CircleSerializer
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.serializers import QuerySerializer


class CreateOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", "inn")


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "inn")
        read_only_fields = fields


class OrganizationInviteSerializer(serializers.Serializer):
    phone = PhoneNumberField(max_length=17, required=True)
    name = serializers.CharField(max_length=255, required=True)
    position = serializers.CharField(max_length=255, required=True)


class InviteEmployeeUpdateSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    name = serializers.CharField(max_length=255, required=False, default=None)
    position = serializers.CharField(max_length=255, required=False, default=None)