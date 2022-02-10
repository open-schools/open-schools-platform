from rest_framework import serializers

from models.models import UserProfile


class CreateUserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model=UserProfile
        fields=('phone_number',)

