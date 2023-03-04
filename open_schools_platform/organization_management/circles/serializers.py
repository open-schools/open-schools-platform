from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.serializers import CircleOrganizationSerializer
from open_schools_platform.organization_management.teachers.serializers import TeacherSerializer
from open_schools_platform.student_management.students.models import Student


class CreateCircleSerializer(serializers.ModelSerializer):
    organization = serializers.UUIDField(required=True)

    class Meta:
        model = Circle
        fields = ('name', 'organization', 'address', 'capacity', 'description')


class CircleSerializer(serializers.ModelSerializer):
    organization = CircleOrganizationSerializer()
    teachers = TeacherSerializer(many=True)

    class Meta:
        model = Circle
        fields = ('id', 'name', 'organization', 'teachers', 'address', 'capacity', 'description', 'latitude',
                  'longitude')


class CircleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = ('id', 'name', 'address', 'latitude', 'longitude')


class QueryCircleRecipientSerializer(serializers.ModelSerializer):
    organization = CircleOrganizationSerializer()

    class Meta:
        model = Circle
        fields = ('id', 'name', 'organization', 'address')


class QueryCircleStudentBodySerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ("name",)


class CircleStudentInviteSerializer(serializers.Serializer):
    body = QueryCircleStudentBodySerializer(required=True)
    student_phone = PhoneNumberField(max_length=17, required=False)
    parent_phone = PhoneNumberField(max_length=17, required=True)
    email = serializers.EmailField(max_length=255, required=True)
