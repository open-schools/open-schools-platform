from rest_framework import serializers

from open_schools_platform.organization_management.employees.models import Employee


class HistoryRecordsField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        return super().to_representation(data.values("history_id", "history_user_id", "history_date", "history_type",
                                                     "id", "name", "employee_profile", "employee_profile",
                                                     "organization_id", "organization", "position",))


class EmployeeHistorySerializer(serializers.ModelSerializer):
    history = HistoryRecordsField(read_only=True)

    class Meta:
        model = Employee
        fields = ("history",)
