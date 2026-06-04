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
    scopes = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)

    class Meta:
        model = Installation
        exclude = ("id", "updated_at", "created_at", "active", "user", "granted_scopes")

    def validate(self, attrs):
        app = attrs.get('app')
        requested_scopes = set(attrs.pop('scopes', []))
        
        required = set(app.required_scopes)
        optional = set(app.optional_scopes)
        
        if not required.issubset(requested_scopes):
            missing = required - requested_scopes
            # If no scopes were provided at all, maybe we just default to required?
            if not requested_scopes:
                requested_scopes = required
            else:
                from open_schools_platform.errors.exceptions import InvalidArgument
                raise InvalidArgument(f"Missing required scopes: {missing}")
                
        # Filter out anything that is neither required nor optional
        final_scopes = requested_scopes.intersection(required.union(optional))
        attrs['granted_scopes'] = " ".join(final_scopes)
        
        return attrs


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
    client_secret = serializers.CharField()
    redirect_uri = serializers.URLField(required=False)