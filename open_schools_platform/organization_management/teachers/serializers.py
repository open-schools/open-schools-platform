from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.teachers.models import TeacherProfile, Teacher
from open_schools_platform.photo_management.photos.serializers import PhotoSerializer


class TeacherProfileSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer()

    class Meta:
        model = TeacherProfile
        fields = ("name", "age", "id", "phone", "photo")


class QueryTeacherBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ("name",)


class CircleTeacherInviteSerializer(serializers.Serializer):
    body = QueryTeacherBodySerializer(required=True)
    phone = PhoneNumberField(max_length=17, required=True)
    email = serializers.EmailField(max_length=255, required=True)


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'name', 'circle', 'teacher_profile')
