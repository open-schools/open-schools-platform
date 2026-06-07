import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status
from drf_yasg.utils import swagger_auto_schema
from django.utils.crypto import get_random_string

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.marketplace_management.models import App, AppStatus


class JiraWebhookSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    ticket_id = serializers.CharField(required=False, allow_blank=True, default="")
    icon_url = serializers.URLField(required=False, allow_blank=True, default="")
    redirect_uris = serializers.ListField(child=serializers.URLField(), required=False, default=list)
    required_scopes = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    optional_scopes = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    def validate_required_scopes(self, value):
        from open_schools_platform.marketplace_management.scopes import AVAILABLE_SCOPES
        invalid_scopes = [s for s in value if s not in AVAILABLE_SCOPES]
        if invalid_scopes:
            raise serializers.ValidationError(f"Invalid required scopes: {', '.join(invalid_scopes)}")
        return value

    def validate_optional_scopes(self, value):
        from open_schools_platform.marketplace_management.scopes import AVAILABLE_SCOPES
        invalid_scopes = [s for s in value if s not in AVAILABLE_SCOPES]
        if invalid_scopes:
            raise serializers.ValidationError(f"Invalid optional scopes: {', '.join(invalid_scopes)}")
        return value


class JiraApproveWebhookView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=JiraWebhookSerializer,
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        operation_description="Webhook for Jira Service Management to publish an App"
    )
    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        expected_secret = getattr(settings, 'JIRA_WEBHOOK_SECRET', '')
        
        if not expected_secret or auth_header != f"Bearer {expected_secret}":
            raise PermissionDenied("Invalid or missing webhook secret")
            
        serializer = JiraWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        client_secret = get_random_string(length=64)
        
        app = App.objects.create(
            name=data["name"],
            description=data["description"],
            icon_url=data.get("icon_url", ""),
            redirect_uris=data.get("redirect_uris", []),
            required_scopes=data.get("required_scopes", []),
            optional_scopes=data.get("optional_scopes", []),
            status=AppStatus.PUBLISHED,
            client_secret=client_secret
        )
        
        return Response({
            "client_id": str(app.client_id),
            "client_secret": client_secret,
            "message": "App successfully published"
        }, status=status.HTTP_201_CREATED)
