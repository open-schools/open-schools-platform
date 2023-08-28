from rest_framework import serializers

from open_schools_platform.photo_management.photos.models import Photo


class GetPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image')


class UpdatePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("image",)
