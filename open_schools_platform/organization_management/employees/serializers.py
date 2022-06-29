from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.serializers import OrganizationSerializer
from open_schools_platform.user_management.users.serializers import UserSerializer


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = EmployeeProfile
        fields = ("id", "user")
        read_only_fields = fields


class EmployeeSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "name", "organization", "position")
        read_only_fields = fields


class EmployeeListSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['phone'] = ret['employee_profile']['user']['phone']
        ret['employee_profile'] = ret['employee_profile']['id']
        return ret

    class Meta:
        model = Employee
        fields = ("id", "name", 'employee_profile', "organization", "position")
        read_only_fields = fields


class CreateEmployeeSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(
        max_length=17,
        required=True,
    )

    class Meta:
        model = Employee
        fields = ("name", "phone", "organization", "position")
