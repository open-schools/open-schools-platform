from re import match
from rest_framework import serializers
from models.models import UserProfile
from services.auth_services import prepare_phone_number


class CreateUserProfileSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    recaptcha = serializers.CharField(allow_null=True, required=False)
    otp = serializers.CharField(allow_null=True, required=False)

    def validate(self, attrs):
        if not match(
                r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$",
                attrs["phone_number"],
        ):
            raise serializers.ValidationError(detail="Invalid phone number")
        attrs["phone_number"] = prepare_phone_number(attrs["phone_number"])
        if "otp" in attrs and not match(r"[0-9]{6}", attrs["otp"]):
            raise serializers.ValidationError(detail="Invalid otp")
        return True

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
