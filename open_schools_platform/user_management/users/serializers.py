from re import match

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.employees.serializers import GetEmployeeProfileSerializer
from open_schools_platform.organization_management.teachers.serializers import GetTeacherProfileSerializer
from open_schools_platform.parent_management.parents.serializers import GetParentProfileSerializer
from open_schools_platform.student_management.students.serializers import GetStudentProfileSerializer
from open_schools_platform.user_management.users.models import CreationToken, User


class CreateCreationTokenSerializer(serializers.Serializer):
    phone = PhoneNumberField(
        max_length=17,
        required=True,
    )
    recaptcha = serializers.CharField(
        allow_null=False,
        required=True,
    )


class GetCreationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreationToken
        fields = ("key", "phone", "is_verified")


class OtpSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        if not match(r"[0-9]{6}", attrs["otp"]):
            raise serializers.ValidationError(detail="Invalid otp")
        return attrs


class CreateUserSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
    name = serializers.CharField(max_length=120)
    password = serializers.CharField(min_length=6, max_length=40)


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone", "name")


class GetUserProfilesSerializer(serializers.ModelSerializer):
    parent_profile = GetParentProfileSerializer()
    employee_profile = GetEmployeeProfileSerializer()
    student_profile = GetStudentProfileSerializer()
    teacher_profile = GetTeacherProfileSerializer()

    class Meta:
        model = User
        fields = ("id", "phone", "name", "parent_profile", "employee_profile", "student_profile", "teacher_profile")


class PasswordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("password",)


class ResendSerializer(serializers.Serializer):
    recaptcha = serializers.CharField(
        allow_null=False,
        required=True,
    )


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
    password = serializers.CharField(min_length=6, max_length=40, required=True)


class FCMNotificationToken(serializers.Serializer):
    token = serializers.CharField(required=True)
