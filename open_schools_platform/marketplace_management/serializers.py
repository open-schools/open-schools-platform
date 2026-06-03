from rest_framework import serializers

from open_schools_platform.marketplace_management.models import (
    App,
    Installation,
)


class AppSerializer(serializers.ModelSerializer):

    class Meta:
        model = App
        fields = "__all__"


class InstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installation
        fields = "__all__"


class InstallationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installation
        exclude = ("id", "updated_at", "created_at", "active", "user")


class InstallationListSerializer(serializers.ModelSerializer):
    school = serializers.SerializerMethodField()
    app = serializers.SerializerMethodField()
    status = serializers.BooleanField(source="active")

    def get_school(self, obj):
        return {
            "id": str(obj.organization.id),
            "name": obj.organization.name
        }

    def get_app(self, obj):
        return {
            "id": str(obj.app.id),
            "name": obj.app.name
        }

    class Meta:
        model = Installation
        fields = ["id", "school", "app", "installed_at", "status"]


class AuthorizeRequestSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()
    response_type = serializers.CharField()
    redirect_uri = serializers.URLField()
    scope = serializers.CharField(required=False, allow_blank=True, default="")
    state = serializers.CharField(required=False, allow_blank=True, default="")


class TokenRequestSerializer(serializers.Serializer):
    grant_type = serializers.CharField()
    code = serializers.CharField()
    client_id = serializers.UUIDField()
    client_secret = serializers.CharField(required=False, allow_blank=True, default="")
    redirect_uri = serializers.URLField(required=False)