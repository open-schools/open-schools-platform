from django.core.validators import MinValueValidator
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.photo_management.photos.serializers import PhotoSerializer
from open_schools_platform.student_management.students.models import StudentProfile, Student, \
    StudentProfileCircleAdditional


class QueryStudentBodySerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('name',)


class QueryStudentBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'name')


class QueryStudentProfileSenderSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer()

    class Meta:
        model = StudentProfile
        fields = ('id', 'photo')


class StudentProfileSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer()

    class Meta:
        model = StudentProfile
        fields = ("name", "age", "id", "phone", "photo")


class StudentSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer()

    class Meta:
        model = Student
        fields = ("id", "name", "circle", "student_profile")


class QueryStudentProfileAdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfileCircleAdditional
        fields = ("parent_phone", "parent_name", "student_phone", "text")


class CreateQueryStudentProfileAdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfileCircleAdditional
        fields = ("text",)


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    family = serializers.UUIDField(required=True)

    class Meta:
        model = StudentProfile
        fields = ("age", "name", "family", "phone")
        extra_kwargs = {"phone": {'required': False}}


class StudentProfileCreateSerializerForQuery(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("age", "name", "phone")
        extra_kwargs = {"phone": {'required': False}}


class StudentProfileUpdateSerializer(serializers.Serializer):
    family = serializers.UUIDField(default=None, required=False)
    name = serializers.CharField(max_length=200, required=False, default=None)
    age = serializers.IntegerField(validators=[MinValueValidator(0)], required=False, default=None)
    phone = PhoneNumberField(max_length=17, required=False)
    photo = serializers.FileField(required=False)


class AutoStudentJoinCircleQuerySerializer(serializers.Serializer):
    circle = serializers.UUIDField(required=True)
    additional = CreateQueryStudentProfileAdditionalSerializer(required=True)
    student_profile = StudentProfileCreateSerializerForQuery(required=True)


class StudentJoinCircleQuerySerializer(serializers.Serializer):
    circle = serializers.UUIDField(required=True)
    additional = CreateQueryStudentProfileAdditionalSerializer(required=True)


class StudentJoinCircleQueryUpdateSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    body = QueryStudentBodySerializerUpdate()
