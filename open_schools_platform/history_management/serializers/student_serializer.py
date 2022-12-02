from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import HistoryFields
from open_schools_platform.student_management.students.models import Student, StudentProfile


class StudentHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(
        fields=HistoryFields().HISTORY_STUDENT_FIELDS)(read_only=True)

    class Meta:
        model = Student
        fields = ("history",)


class StudentProfileHistorySerializer(serializers.ModelSerializer):
    history = HistoryFields.get_history_records_field(
        fields=HistoryFields().HISTORY_STUDENT_PROFILES_FIELDS)(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("history", )
