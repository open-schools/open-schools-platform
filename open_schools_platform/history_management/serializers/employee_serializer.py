from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile


class EmployeeHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_EMPLOYEE_FIELDS)(read_only=True)

    class Meta:
        model = Employee
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(fields=HistorySerializerFields().HISTORY_EMPLOYEE_FIELDS,
                                                               object_title='EmployeeHistory',
                                                               model=Employee).generate_schemas()


class EmployeeProfileHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_EMPLOYEE_PROFILE_FIELDS)(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(
            fields=HistorySerializerFields().HISTORY_EMPLOYEE_PROFILE_FIELDS,
            object_title='EmployeeProfileHistory',
            model=EmployeeProfile).generate_schemas()
