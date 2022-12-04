from rest_framework import serializers

from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.photo_management.photos.serializers import PhotoSerializer


class TeacherProfileSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer()

    class Meta:
        model = TeacherProfile
        fields = ("name", "age", "id", "phone", "photo")
