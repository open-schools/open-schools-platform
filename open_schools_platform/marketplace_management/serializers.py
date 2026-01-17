from typing import Union

from rest_framework import serializers

from open_schools_platform.marketplace_management.models import (
    AppRelease,
    App,
    Category,
    Installation,
    Review,
    InstallationStatus,
)


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("app", "rating", "message")

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class ReviewListSerializer(serializers.ModelSerializer):
    user: serializers.StringRelatedField = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "rating",
            "message",
            "created_at",
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

    avg_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    def get_latest_published_release(self, obj: App) -> Union[dict, None]:
        latest_version = AppRelease.objects.filter(app=obj).order_by("-date").first()
        if latest_version:
            return AppReleaseSerializer(latest_version).data
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
        exclude = (
            "id",
            "updated_at",
            "created_at",
            "active",
            "user",
            "installed_at",
            "disabled_at",
            "status",
            "re_activated_at",
            "uninstalled_at",
        )


class InstallationListSerializer(serializers.ModelSerializer):
    school = serializers.SerializerMethodField()
    app = serializers.SerializerMethodField()
    status = serializers.BooleanField(source="active")

    def get_school(self, obj):
        return {"id": str(obj.organization.id), "name": obj.organization.name}

    def get_app(self, obj):
        return {"id": str(obj.app.id), "name": obj.app.name}

    class Meta:
        model = Installation
        fields = ["id", "school", "app", "installed_at", "status"]


class InstallationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=InstallationStatus.choices)
