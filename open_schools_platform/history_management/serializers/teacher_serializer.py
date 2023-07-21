from rest_framework import serializers

from open_schools_platform.history_management.serializers.history_serializer import BaseHistorySerializer
from open_schools_platform.organization_management.teachers.models import Teacher, TeacherProfile


class GetTeacherHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = Teacher
        fields = (
            'id', 'name', 'circle', 'teacher_profile', 'history_id', 'history_user_id', 'history_date', 'history_type')


class GetTeacherProfileHistorySerializer(serializers.ModelSerializer, BaseHistorySerializer):
    class Meta:
        model = TeacherProfile
        fields = (
            'id', 'name', 'phone', 'age', 'photo', 'history_id', 'history_user_id', 'history_date', 'history_type')
