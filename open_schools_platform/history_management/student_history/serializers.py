from rest_framework import serializers

from open_schools_platform.student_management.students.models import Student


class HistoryRecordsField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        return super().to_representation(data.values("history_id", "history_user_id", "history_date", "history_type",
                                                     "id", "name", "circle_id", "student_profile_id",))


class StudentHistorySerializer(serializers.ModelSerializer):
    history = HistoryRecordsField(read_only=True)

    class Meta:
        model = Student
        fields = ("history",)
