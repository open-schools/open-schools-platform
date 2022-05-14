from rest_framework import serializers

from open_schools_platform.employee_management.employees.models import Employee


class CreateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("name", "user", "organization", "position")
