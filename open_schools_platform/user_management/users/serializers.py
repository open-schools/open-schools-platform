from re import match

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.user_management.users.models import CreationToken, User


class CreationTokenSerializer(serializers.Serializer):
    phone = PhoneNumberField(
        max_length=17,
        required=True,
    )
    recaptcha = serializers.CharField(
        allow_null=False,
        required=True,
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RetrieveCreationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreationToken
        fields = ("key", "phone", "is_verified")


class OtpSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        if not match(r"[0-9]{6}", attrs["otp"]):
            raise serializers.ValidationError(detail="Invalid otp")
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserRegisterSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
    name = serializers.CharField(max_length=120)
    password = serializers.CharField(min_length=6, max_length=40)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "phone", "name"]


class PasswordUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["password"]


class ResendSerializer(serializers.Serializer):
    recaptcha = serializers.CharField(
        allow_null=False,
        required=True,
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
    password = serializers.CharField(min_length=6, max_length=40)
