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
    app_url = serializers.URLField(required=False, allow_blank=True, default="")
    redirect_uris = serializers.ListField(child=serializers.URLField(), required=False, default=list)
    required_scopes = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    optional_scopes = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    category_name = serializers.CharField(required=False, allow_blank=True, default="")
    privacy_policy_url = serializers.URLField(required=False, allow_blank=True, default="")
    eula_url = serializers.URLField(required=False, allow_blank=True, default="")

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
        
        category = None
        category_name = data.get("category_name")
        if category_name:
            from open_schools_platform.marketplace_management.models import Category
            category, _ = Category.objects.get_or_create(name=category_name)
        
        app = App.objects.create(
            name=data["name"],
            description=data["description"],
            icon_url=data.get("icon_url", ""),
            app_url=data.get("app_url", ""),
            redirect_uris=data.get("redirect_uris", []),
            required_scopes=data.get("required_scopes", []),
            optional_scopes=data.get("optional_scopes", []),
            status=AppStatus.PUBLISHED,
            client_secret=client_secret,
            category=category,
            privacy_policy_url=data.get("privacy_policy_url", ""),
            eula_url=data.get("eula_url", "")
        )
        
        return Response({
            "client_id": str(app.client_id),
            "client_secret": client_secret,
            "message": "App successfully published"
        }, status=status.HTTP_201_CREATED)


class ValidateCredentialsSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()
    client_secret = serializers.CharField()


class ValidateCredentialsWebhookView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=ValidateCredentialsSerializer,
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        operation_description="Webhook for JSM to validate app credentials"
    )
    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        expected_secret = getattr(settings, 'JIRA_WEBHOOK_SECRET', '')
        
        if not expected_secret or auth_header != f"Bearer {expected_secret}":
            raise PermissionDenied("Invalid or missing webhook secret")
            
        serializer = ValidateCredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            app = App.objects.get(client_id=data["client_id"])
        except App.DoesNotExist:
            raise PermissionDenied("Invalid Client ID or Client Secret")
            
        if not app.client_secret:
            raise PermissionDenied("Invalid Client ID or Client Secret")

        from django.contrib.auth.hashers import check_password
        if not check_password(data["client_secret"], app.client_secret) and data["client_secret"] != app.client_secret:
             raise PermissionDenied("Invalid Client ID or Client Secret")
             
        return Response({"message": "Credentials are valid"}, status=status.HTTP_200_OK)


class JiraUpdateAppSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    icon_url = serializers.URLField(required=False, allow_blank=True)
    app_url = serializers.URLField(required=False, allow_blank=True)
    redirect_uris = serializers.ListField(child=serializers.URLField(), required=False)
    category_name = serializers.CharField(required=False, allow_blank=True)
    privacy_policy_url = serializers.URLField(required=False, allow_blank=True)
    eula_url = serializers.URLField(required=False, allow_blank=True)


class JiraUpdateAppWebhookView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=JiraUpdateAppSerializer,
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        operation_description="Webhook for JSM to update an App"
    )
    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        expected_secret = getattr(settings, 'JIRA_WEBHOOK_SECRET', '')
        
        if not expected_secret or auth_header != f"Bearer {expected_secret}":
            raise PermissionDenied("Invalid or missing webhook secret")
            
        serializer = JiraUpdateAppSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            app = App.objects.get(client_id=data["client_id"])
        except App.DoesNotExist:
            return Response({"error": "App not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Update fields that were provided
        for field in ["name", "description", "icon_url", "app_url", "redirect_uris", "privacy_policy_url", "eula_url"]:
            if field in data:
                setattr(app, field, data[field])
                
        if "category_name" in data:
            if data["category_name"]:
                from open_schools_platform.marketplace_management.models import Category
                category, _ = Category.objects.get_or_create(name=data["category_name"])
                app.category = category
            else:
                app.category = None
                
        app.save()
        
        return Response({"message": "App successfully updated"}, status=status.HTTP_200_OK)


class JiraDeleteAppSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()


class JiraDeleteAppWebhookView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=JiraDeleteAppSerializer,
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        operation_description="Webhook for JSM to delete an App"
    )
    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        expected_secret = getattr(settings, 'JIRA_WEBHOOK_SECRET', '')
        
        if not expected_secret or auth_header != f"Bearer {expected_secret}":
            raise PermissionDenied("Invalid or missing webhook secret")
            
        serializer = JiraDeleteAppSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            app = App.objects.get(client_id=data["client_id"])
        except App.DoesNotExist:
            return Response({"error": "App not found"}, status=status.HTTP_404_NOT_FOUND)
            
        app.delete()
        
        return Response({"message": "App successfully deleted"}, status=status.HTTP_200_OK)
