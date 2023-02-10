from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.student_management.students.models import Student, StudentProfile


class StudentHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_STUDENT_FIELDS)(read_only=True)

    class Meta:
        model = Student
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(fields=HistorySerializerFields().HISTORY_STUDENT_FIELDS,
                                                               object_title='StudentHistory',
                                                               model=Student).generate_schemas()


class StudentProfileHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_STUDENT_PROFILE_FIELDS)(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(
            fields=HistorySerializerFields().HISTORY_STUDENT_PROFILE_FIELDS,
            object_title='StudentProfileHistory',
            model=StudentProfile).generate_schemas()
