from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile


class EmployeeHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = Employee
        fields = (
            'id', 'name', 'organization', 'position', 'history_id', 'history_user_id', 'history_date', 'history_type')


class EmployeeProfileHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = EmployeeProfile
        fields = (
            'id', 'name', 'user', 'history_id', 'history_user_id', 'history_date', 'history_type')
