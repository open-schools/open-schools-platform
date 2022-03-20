from re import match

from django.core.validators import RegexValidator
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


class UserSerializer(serializers.Serializer):
    phone = PhoneNumberField(
        max_length=17,
        required=True,
    )
