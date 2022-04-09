from rest_framework import serializers

from registration.models import UserProfile


class CreateUserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model=UserProfile
        fields=('phone_number',)

