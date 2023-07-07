from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.student_management.students.models import Student, StudentProfile


class StudentHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = Student
        fields = (
            'id', 'name', 'circle', 'student_profile', 'history_id', 'history_user_id', 'history_date', 'history_type')


class StudentProfileHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = StudentProfile
        fields = (
            'id', 'name', 'phone', 'age', 'photo', 'history_id', 'history_user_id', 'history_date', 'history_type')
