from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.serializers import \
    GetOrganizationSerializer
from open_schools_platform.user_management.users.models import User


class GetEmployeeProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone", "name")


class GetEmployeeProfileWithUserSerializer(serializers.ModelSerializer):
    user = GetEmployeeProfileUserSerializer()

    class Meta:
        model = EmployeeProfile
        fields = ("id", "name", "user")
        read_only_fields = fields


class GetEmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ("id", "name", "user")


class GetEmployeeProfileRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ("id", "name", "user")


class GetEmployeeSerializer(serializers.ModelSerializer):
    organization = GetOrganizationSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "name", "organization", "position")
        read_only_fields = fields


class UpdateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("name",)


class GetEmployeeBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("name", "position")


class GetEmployeeListSerializer(serializers.ModelSerializer):
    employee_profile = GetEmployeeProfileWithUserSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['phone'] = ret['employee_profile']['user']['phone']
        ret['employee_profile'] = ret['employee_profile']['id']
        return ret

    class Meta:
        model = Employee
        fields = ("id", "name", 'employee_profile', "organization", "position")
        read_only_fields = fields


class CreateOrganizationInviteEmployeeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    phone = PhoneNumberField(max_length=17, required=True)
    body = GetEmployeeBodySerializer(required=True)


class UpdateOrganizationInviteEmployeeSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    body = GetEmployeeBodySerializer(required=True)
