from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status

from .serializers import JSONWebTokenWithTwoResponses

from rest_framework_jwt.views import BaseJSONWebTokenAPIView

from open_schools_platform.api.mixins import ApiAuthMixin

from open_schools_platform.user_management.authentication.services import auth_logout

from open_schools_platform.user_management.users.selectors import user_get_login_data


class UserSessionLoginApi(APIView):
    """
    Following https://docs.djangoproject.com/en/3.1/topics/auth/default/#how-to-log-a-user-in
    """
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    @swagger_auto_schema(
        tags=['User management. Authentication']
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request, **serializer.validated_data)

        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        data = user_get_login_data(user=user)
        session_key = request.session.session_key

        return Response({
            'session': session_key,
            'data': data
        })


class UserSessionLogoutApi(APIView):
    @swagger_auto_schema(
        tags=['User management. Authentication']
    )
    def get(self, request):
        logout(request)

        return Response()

    @swagger_auto_schema(
        tags=['User management. Authentication']
    )
    def post(self, request):
        logout(request)

        return Response()


class UserJwtLoginApi(BaseJSONWebTokenAPIView):
    serializer_class = JSONWebTokenWithTwoResponses

    @swagger_auto_schema(
        tags=['User management. Authentication']
    )
    def post(self, request, *args, **kwargs):
        # We are redefining post so we can change the response status on success
        # Mostly for consistency with the session-based API
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            response.status_code = status.HTTP_200_OK

        return response


class UserJwtLogoutApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=['User management. Authentication']
    )
    def post(self, request):
        auth_logout(request.user)

        response = Response()

        if settings.JWT_AUTH['JWT_AUTH_COOKIE'] is not None:
            response.delete_cookie(settings.JWT_AUTH['JWT_AUTH_COOKIE'])

        return response


class UserMeApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        tags=['User management. Authentication']
    )
    def get(self, request):
        data = user_get_login_data(user=request.user)

        return Response(data)
