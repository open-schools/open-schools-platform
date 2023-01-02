from django.core.validators import MinValueValidator
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.common.serializers import get_serializer_with_fields
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.photo_management.photos.serializers import PhotoSerializer
from open_schools_platform.student_management.students.models import StudentProfile, Student, \
    StudentProfileCircleAdditional


class QueryStudentBodySerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('name',)


class QueryStudentBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'name')


class QueryStudentProfileSenderSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer()

    class Meta:
        model = StudentProfile
        fields = ('id', 'photo')


class StudentProfileSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer()

    class Meta:
        model = StudentProfile
        fields = ("name", "age", "id", "phone", "photo")


class StudentSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer()

    class Meta:
        model = Student
        fields = ("id", "name", "circle", "student_profile")


class QueryStudentProfileAdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfileCircleAdditional
        fields = ("parent_phone", "parent_name", "student_phone", "text")


class CreateQueryStudentProfileAdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfileCircleAdditional
        fields = ("text",)


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    family = serializers.UUIDField(required=True)

    class Meta:
        model = StudentProfile
        fields = ("age", "name", "family", "phone")
        extra_kwargs = {"phone": {'required': False}}


class StudentProfileAddPhotoSerializer(serializers.Serializer):
    photo = serializers.FileField(required=True)


class StudentProfileCreateSerializerForQuery(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("age", "name", "phone")
        extra_kwargs = {"phone": {'required': False}}


class StudentProfileUpdateSerializer(serializers.Serializer):
    family = serializers.UUIDField(default=None, required=False)
    name = serializers.CharField(max_length=200, required=False, default=None)
    age = serializers.IntegerField(validators=[MinValueValidator(0)], required=False, default=None)
    phone = PhoneNumberField(max_length=17, required=False)


class AutoStudentJoinCircleQuerySerializer(serializers.Serializer):
    circle = serializers.UUIDField(required=True)
    additional = CreateQueryStudentProfileAdditionalSerializer(required=True)
    student_profile = StudentProfileCreateSerializerForQuery(required=True)


class StudentJoinCircleQuerySerializer(serializers.Serializer):
    circle = serializers.UUIDField(required=True)
    additional = CreateQueryStudentProfileAdditionalSerializer(required=True)


class StudentJoinCircleQueryUpdateSerializer(serializers.Serializer):
    query = serializers.UUIDField(required=True)
    body = QueryStudentBodySerializerUpdate()


class StudentGetSerializer(serializers.ModelSerializer):
    student_profile = get_serializer_with_fields(StudentProfileSerializer, fields=('phone', 'photo'))

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        families = instance.student_profile.families.all()
        parent = get_parent_profile(filters={"families": form_ids_string_from_queryset(families)})
        representation['parent_phone'] = str(parent.user.phone)
        return representation

    class Meta:
        model = Student
        fields = ["id", "name", "student_profile"]
