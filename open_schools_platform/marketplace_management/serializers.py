from rest_framework import serializers

from open_schools_platform.marketplace_management.models import (
    App,
    Installation,
    Review,
)


class AppSerializer(serializers.ModelSerializer):

    class Meta:
        model = App
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return str(obj.user.name if hasattr(obj.user, 'name') and obj.user.name else obj.user.phone)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "message", "created_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "message"]



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
    code = serializers.CharField(required=False)
    refresh_token = serializers.CharField(required=False)
    client_id = serializers.UUIDField()
    client_secret = serializers.CharField()
    redirect_uri = serializers.URLField(required=False)

    def validate(self, attrs):
        grant_type = attrs.get('grant_type')
        if grant_type == 'authorization_code':
            if not attrs.get('code'):
                raise serializers.ValidationError("code is required for authorization_code grant type")
        elif grant_type == 'refresh_token':
            if not attrs.get('refresh_token'):
                raise serializers.ValidationError("refresh_token is required for refresh_token grant type")
        else:
            raise serializers.ValidationError("Unsupported grant_type")
        return attrs


class RevokeTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    client_id = serializers.UUIDField()
    client_secret = serializers.CharField()