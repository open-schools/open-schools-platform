from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization


class CreateOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", 'inn')
        extra_kwargs = {"name": {'required': True}}


class GetOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "inn")
        read_only_fields = fields


class GetOrganizationSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "inn")
        read_only_fields = fields


class GetShallowOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class GetAnalyticsSerializer(serializers.Serializer):
    IN_PROGRESS = serializers.IntegerField()
    SENT = serializers.IntegerField()
    ACCEPTED = serializers.IntegerField()
    DECLINED = serializers.IntegerField()
    CANCELED = serializers.IntegerField()


class GetOrganizationCircleListSerializer(serializers.ModelSerializer):
    student_profile_queries = serializers.SerializerMethodField(
        "get_student_profile_queries"
    )

    @swagger_serializer_method(GetAnalyticsSerializer)
    def get_student_profile_queries(self, obj):
        from open_schools_platform.query_management.queries.services import count_queries_by_statuses
        return GetAnalyticsSerializer(count_queries_by_statuses(obj.student_profile_queries)).data

    class Meta:
        model = Circle
        fields = ('id', 'name', 'address', 'student_profile_queries')
