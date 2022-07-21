import uuid

from django.core.validators import MinValueValidator
from rest_framework import serializers

from open_schools_platform.student_management.student.models import StudentProfile


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    family = serializers.UUIDField(default=uuid.uuid4)

    class Meta:
        model = StudentProfile
        fields = ("age", "name", "family")


class StudentProfileUpdateSerializer(serializers.Serializer):
    student_profile = serializers.UUIDField(default=uuid.uuid4)
    family = serializers.UUIDField(default=None, required=False)
    name = serializers.CharField(max_length=200, required=False, default=None)
    age = serializers.IntegerField(validators=[MinValueValidator(0)], required=False, default=None)


class StudentJoinCircleReqSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentProfile
        fields = ("name", "age")


class StudentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentProfile
        fields = ("name", "age", "id")
