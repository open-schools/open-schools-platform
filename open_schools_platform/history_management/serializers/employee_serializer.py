from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistoryFields
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile


class EmployeeHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(fields=HistoryFields().HISTORY_EMPLOYEE_FIELDS)(read_only=True)

    class Meta:
        model = Employee
        fields = ("history",)


class EmployeeProfileHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(
        fields=HistoryFields().HISTORY_EMPLOYEE_PROFILE_FIELDS)(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ("history",)
