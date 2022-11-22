from rest_framework import serializers

from open_schools_platform.history_management.serializers.fields import get_history_records_field
from open_schools_platform.student_management.students.models import Student, StudentProfile


class StudentHistorySerializer(serializers.ModelSerializer):
    history = get_history_records_field(fields=("history_id", "history_user_id", "history_date", "history_type", "id",
                                                "name", "circle", "student_profile",))(read_only=True)

    class Meta:
        model = Student
        fields = ("history",)


class StudentProfileHistorySerializer(serializers.ModelSerializer):
    history = get_history_records_field(fields=("history_id", "history_user_id", "history_date", "history_type", "name",
                                                "age", "id", "phone", "photo"))(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("history", )
