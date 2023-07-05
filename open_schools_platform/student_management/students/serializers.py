from django.core.validators import MinValueValidator
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.common.serializers import BaseModelSerializer
from open_schools_platform.photo_management.photos.serializers import PhotoSerializer
from open_schools_platform.student_management.students.models import StudentProfile, Student, \
    StudentProfileCircleAdditional


class StudentProfileFullSerializer(BaseModelSerializer):
    photo = PhotoSerializer()
    family = serializers.UUIDField(required=True)

    class Meta:
        model = StudentProfile
        fields = ("id", "name", "age", "phone", "photo", "family")


class UpdateStudentProfileSerializer(serializers.Serializer):
    family = serializers.UUIDField(default=None, required=False)
    name = serializers.CharField(max_length=200, required=False, default=None)
    age = serializers.IntegerField(validators=[MinValueValidator(0)], required=False, default=None)
    phone = PhoneNumberField(max_length=17, required=False)


class StudentProfileSerializer(BaseModelSerializer):
    photo = PhotoSerializer()

    class Meta:
        model = StudentProfile
        fields = ("id", "name", "age", "phone", "photo")


class StudentSerializer(BaseModelSerializer):
    student_profile = StudentProfileFullSerializer.with_fields(["id", "name", "age", "phone", "photo"])()

    class Meta:
        model = Student
        fields = ("id", "name", "circle", "student_profile")


class StudentProfileAdditionalSerializer(BaseModelSerializer):
    class Meta:
        model = StudentProfileCircleAdditional
        fields = ("parent_phone", "parent_name", "student_phone", "text")


class AutoStudentJoinCircleQuerySerializer(serializers.Serializer):
    circle = serializers.UUIDField(required=True)
    additional = StudentProfileAdditionalSerializer.with_fields(["text"])(required=True)
    student_profile = StudentProfileFullSerializer.with_fields(["age", "name", "phone"])(required=True)


class StudentJoinCircleQuerySerializer(serializers.Serializer):
    circle = serializers.UUIDField(required=True)
    additional = StudentProfileAdditionalSerializer.with_fields(["text"])(required=True)


class StudentJoinCircleQueryUpdateSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    body = StudentSerializer.with_fields(['name'])()
