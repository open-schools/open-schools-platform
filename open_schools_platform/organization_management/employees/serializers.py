from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.employees.models import Employee


class RetrieveEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("pk", "name", "user", "organization", "position")


class CreateEmployeeSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(
        max_length=17,
        required=True,
    )

    class Meta:
        model = Employee
        fields = ("name", "phone", "organization", "position")
