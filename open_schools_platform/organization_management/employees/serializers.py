from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.organizations.serializers import OrganizationSerializer
from open_schools_platform.user_management.users.serializers import UserSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "name", "user", "organization", "position")
        read_only_fields = fields


class CreateEmployeeSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(
        max_length=17,
        required=True,
    )

    class Meta:
        model = Employee
        fields = ("name", "phone", "organization", "position")
