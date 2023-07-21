from rest_framework import serializers

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


class GetCircleOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class GetAnalyticsSerializer(serializers.Serializer):
    IN_PROGRESS = serializers.IntegerField()
    SENT = serializers.IntegerField()
    ACCEPTED = serializers.IntegerField()
    DECLINED = serializers.IntegerField()
    CANCELED = serializers.IntegerField()
