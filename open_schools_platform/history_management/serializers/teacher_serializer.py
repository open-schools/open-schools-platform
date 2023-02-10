from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistorySerializerFields
from open_schools_platform.history_management.swagger_schemas_generator import SwaggerSchemasHistoryGenerator
from open_schools_platform.organization_management.teachers.models import Teacher, TeacherProfile


class TeacherHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_TEACHER_FIELDS)(read_only=True)

    class Meta:
        model = Teacher
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(fields=HistorySerializerFields().HISTORY_TEACHER_FIELDS,
                                                               object_title='TeacherHistory',
                                                               model=Teacher).generate_schemas()


class TeacherProfileHistorySerializer(serializers.ModelSerializer):
    history = HistorySerializerFields.get_history_records_field(
        fields=HistorySerializerFields().HISTORY_TEACHER_PROFILE_FIELDS)(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ("history",)
        swagger_schema_fields = SwaggerSchemasHistoryGenerator(
            fields=HistorySerializerFields().HISTORY_TEACHER_PROFILE_FIELDS,
            object_title='TeacherProfileHistory',
            model=TeacherProfile).generate_schemas()
