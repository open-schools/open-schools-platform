from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.serializers import OrganizationSerializer
from open_schools_platform.user_management.users.models import User


class EmployeeProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone", "name")


class EmployeeProfileWithUserSerializer(serializers.ModelSerializer):
    user = EmployeeProfileUserSerializer()

    class Meta:
        model = EmployeeProfile
        fields = ("id", "name", "user")
        read_only_fields = fields


class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ("id", "name", "user")


class EmployeeSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "name", "organization", "position")
        read_only_fields = fields


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("name",)


class QueryEmployeeBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("name", "position")


class EmployeeListSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileWithUserSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['phone'] = ret['employee_profile']['user']['phone']
        ret['employee_profile'] = ret['employee_profile']['id']
        return ret

    class Meta:
        model = Employee
        fields = ("id", "name", 'employee_profile', "organization", "position")
        read_only_fields = fields


class OrganizationEmployeeInviteSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    phone = PhoneNumberField(max_length=17, required=True)
    body = QueryEmployeeBodySerializer(required=True)


class OrganizationEmployeeInviteUpdateSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    body = QueryEmployeeBodySerializer(required=True)
