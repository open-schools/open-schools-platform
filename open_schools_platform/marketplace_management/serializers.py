from rest_framework import serializers

from open_schools_platform.marketplace_management.models import AppRelease, App, Category


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

    def get_latest_published_release(self, obj: App) -> AppReleaseSerializer | None:
        latest_version = AppRelease.objects.filter(app=obj).order_by("-date").first()
        if latest_version:
            return AppReleaseSerializer(latest_version)
        return None

    class Meta:
        model = App
        fields = "__all__"
