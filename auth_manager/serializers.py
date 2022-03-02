from re import match
from rest_framework import serializers
from auth_manager.utils.sender_sms import prepare_phone_number
from models.models import UserProfile


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
        if "otp" in attrs and match(r"[0-9]{6}", attrs["otp"]):
            raise serializers.ValidationError(detail="Invalid otp")
        return True

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class VerificationCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model=UserProfile
        fields=('verification_code',)
