from django.contrib.gis.geos import GEOSGeometry
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.serializers import CircleOrganizationSerializer
from open_schools_platform.organization_management.teachers.serializers import TeacherSerializer
from open_schools_platform.student_management.students.models import Student


def validate_geometry_string(string):
    try:
        GEOSGeometry(string)
    except Exception:
        raise ValidationError('String input unrecognized as valid geometry format such as WKT EWKT, and HEXEWKB.',
                              code='invalid_geometry')


class CreateCircleSerializer(serializers.ModelSerializer):
    organization = serializers.UUIDField(required=True)
    location = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     validators=[validate_geometry_string])

    class Meta:
        model = Circle
        fields = ('name', 'organization', 'address', 'capacity', 'description', 'location')


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
