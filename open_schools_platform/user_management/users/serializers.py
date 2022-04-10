from re import match

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


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


class OtpSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
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
    password_confirm = serializers.CharField(min_length=6, max_length=40)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(detail="passwords do not match")
        return attrs


class UserSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    name = serializers.CharField(max_length=120)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
