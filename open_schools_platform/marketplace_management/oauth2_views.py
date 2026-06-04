from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.errors.exceptions import InvalidArgument
from rest_framework.exceptions import PermissionDenied
from open_schools_platform.marketplace_management.models import App, OAuth2Token, Installation
from open_schools_platform.marketplace_management.serializers import AuthorizeRequestSerializer, TokenRequestSerializer, RevokeTokenSerializer
from open_schools_platform.marketplace_management.oauth2_services import (
    create_authorization_code, 
    exchange_code_for_token, 
    exchange_refresh_token,
    revoke_token,
    check_installation_exists
)
from open_schools_platform.marketplace_management.scopes import AVAILABLE_SCOPES


class AuthorizeView(ApiAuthMixin, APIView):
    @swagger_auto_schema(query_serializer=AuthorizeRequestSerializer, tags=[SwaggerTags.MARKETPLACE_MANAGEMENT])
    def get(self, request, *args, **kwargs):
        serializer = AuthorizeRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        if data["response_type"] != "code":
            raise InvalidArgument("Unsupported response_type. Only 'code' is supported.")
            
        try:
            app = App.objects.get(client_id=data["client_id"])
        except App.DoesNotExist:
            raise InvalidArgument("Invalid client_id")
            
        if app.redirect_uris and data["redirect_uri"] not in app.redirect_uris:
            raise InvalidArgument("Invalid redirect_uri")
            
        # Fetch Installation to check scopes
        try:
            # We already know installation exists from check_installation_exists,
            # but we need the exact instance to get granted_scopes.
            # Usually the user installing it is in the organization, so we check both cases.
            installation = Installation.objects.filter(app=app, user=request.user, active=True).first()
            if not installation:
                installation = Installation.objects.filter(
                    app=app, organization__employees__employee_profile__user=request.user, active=True
                ).first()
            if not installation:
                raise PermissionDenied("App is not installed for this user or their organization.")
        except Exception:
            raise PermissionDenied("App is not installed.")
            
        requested_scope = data.get("scope", "")
        granted_scopes = set(installation.granted_scopes.split())
        
        for s in requested_scope.split():
            if s and s not in AVAILABLE_SCOPES:
                raise InvalidArgument(f"Invalid scope requested: {s}")
            if s and s not in granted_scopes:
                raise PermissionDenied(f"App is not allowed to request scope: {s}")
            
        # Generate code
        auth_code = create_authorization_code(
            app=app,
            user=request.user,
            redirect_uri=data["redirect_uri"],
            scope=data.get("scope", "")
        )
        
        # Redirect
        redirect_url = f"{data['redirect_uri']}?code={auth_code.code}"
        if data.get("state"):
            redirect_url += f"&state={data['state']}"
            
        return HttpResponseRedirect(redirect_url)


class TokenView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=TokenRequestSerializer, tags=[SwaggerTags.MARKETPLACE_MANAGEMENT])
    def post(self, request, *args, **kwargs):
        serializer = TokenRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        if data["grant_type"] == "authorization_code":
            token_data = exchange_code_for_token(data["code"], str(data["client_id"]), data["client_secret"])
        elif data["grant_type"] == "refresh_token":
            token_data = exchange_refresh_token(data["refresh_token"], str(data["client_id"]), data["client_secret"])
        else:
            raise InvalidArgument("Unsupported grant_type.")
            
        return Response(token_data, status=status.HTTP_200_OK)


class RevokeTokenView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=RevokeTokenSerializer, tags=[SwaggerTags.MARKETPLACE_MANAGEMENT])
    def post(self, request, *args, **kwargs):
        serializer = RevokeTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        revoke_token(data["token"], str(data["client_id"]), data["client_secret"])
        return Response({}, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(tags=[SwaggerTags.MARKETPLACE_MANAGEMENT])
    def get(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            raise PermissionDenied("Missing or invalid authorization header")
            
        token_str = auth_header.split(' ')[1]
        try:
            token = OAuth2Token.objects.select_related('user', 'user__employee_profile').get(access_token=token_str, revoked=False)
        except OAuth2Token.DoesNotExist:
            raise PermissionDenied("Invalid or expired token")
            
        user = token.user
        profile = getattr(user, 'employee_profile', None)
        granted_scopes = set(token.scope.split())
        
        data = {}
        if "openid" in granted_scopes:
            data["sub"] = str(user.id)
        if "phone" in granted_scopes:
            data["phone"] = str(user.phone) if hasattr(user, 'phone') else ""
        if "profile" in granted_scopes:
            data["name"] = profile.name if profile else ""
        if "email" in granted_scopes:
            data["email"] = profile.email if profile and hasattr(profile, 'email') else ""
            
        return Response(data, status=status.HTTP_200_OK)
