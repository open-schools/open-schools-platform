from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import get_history_records_field
from open_schools_platform.organization_management.employees.models import Employee


class EmployeeHistorySerializer(serializers.ModelSerializer):
    history = get_history_records_field(fields=("history_id", "history_user_id", "history_date", "history_type", "id",
                                                "name", "employee_profile", "employee_profile", "organization_id",
                                                "organization", "position",))(read_only=True)

    class Meta:
        model = Employee
        fields = ("history",)
