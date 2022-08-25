import uuid

from django.core.validators import MinValueValidator
from rest_framework import serializers

from open_schools_platform.student_management.students.models import StudentProfile, Student


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    family = serializers.UUIDField(required=True)

    class Meta:
        model = StudentProfile
        fields = ("age", "name", "family")


class StudentProfileUpdateSerializer(serializers.Serializer):
    student_profile = serializers.UUIDField(default=uuid.uuid4)
    family = serializers.UUIDField(default=None, required=False)
    name = serializers.CharField(max_length=200, required=False, default=None)
    age = serializers.IntegerField(validators=[MinValueValidator(0)], required=False, default=None)


class AutoStudentJoinCircleQuerySerializer(serializers.ModelSerializer):
    circle = serializers.UUIDField()

    class Meta:
        model = StudentProfile
        fields = ("name", "age", "circle")


class StudentJoinCircleQuerySerializer(serializers.Serializer):
    circle = serializers.UUIDField()


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("name", "age", "id")


class StudentJoinCircleQueryUpdateSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    name = serializers.CharField(required=False, default=None)


class QueryStudentBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'name')


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("id", "name", "circle")
