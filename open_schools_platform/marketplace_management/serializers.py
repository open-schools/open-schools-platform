from typing import Union

from rest_framework import serializers

from open_schools_platform.marketplace_management.models import (
    AppRelease,
    App,
    Category,
    Installation,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class AppReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppRelease
        exclude = ["app"]


class AppSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    latest_published_release = serializers.SerializerMethodField()

    def get_latest_published_release(self, obj: App) -> Union[AppReleaseSerializer, None]:
        latest_version = AppRelease.objects.filter(app=obj).order_by("-date").first()
        if latest_version:
            return AppReleaseSerializer(latest_version)
        return None

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


class InstallationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Installation.STATUS_CHOICES)
