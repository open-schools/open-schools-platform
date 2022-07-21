from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import JSONWebTokenWithTwoResponses, PasswordUpdateSerializer, UserUpdateSerializer

from rest_framework_jwt.views import BaseJSONWebTokenAPIView

from open_schools_platform.api.mixins import ApiAuthMixin

from open_schools_platform.user_management.authentication.services import auth_logout


from open_schools_platform.api.swagger_tags import SwaggerTags
from ..users.selectors import get_user
from ..users.serializers import UserSerializer, UserWithProfilesSerializer
from ..users.services import set_new_password_for_user, user_update


class UserJwtLoginApi(BaseJSONWebTokenAPIView):
    serializer_class = JSONWebTokenWithTwoResponses

    @swagger_auto_schema(
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH]
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
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH]
    )
    def post(self, request):
        auth_logout(request.user)

        response = Response()

        if settings.JWT_AUTH['JWT_AUTH_COOKIE'] is not None:
            response.delete_cookie(settings.JWT_AUTH['JWT_AUTH_COOKIE'])

        return response


class UserMeApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Get user data.",
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH],
        responses={200: UserWithProfilesSerializer},
    )
    def get(self, request):
        return Response(UserWithProfilesSerializer(request.user).data, status=200)

    @swagger_auto_schema(
        operation_description="Update user.",
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH],
        request_body=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request):
        user = get_user(request)
        user_serializer = UserUpdateSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_update(user=user, data=user_serializer.validated_data)
        return Response(UserSerializer(user).data)


class UpdatePasswordApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Update user password.",
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH],
        request_body=PasswordUpdateSerializer,
        responses={200: "Password was successfully updated."},
    )
    def put(self, request):
        user_serializer = PasswordUpdateSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = get_user(request)

        old_password = user_serializer.validated_data['old_password']
        new_password = user_serializer.validated_data['new_password']

        if not user.check_password(old_password):
            raise AuthenticationFailed(detail="Old password does not match with actual one.")
        if old_password == new_password:
            raise AuthenticationFailed(detail="New password matches with the old one.")

        set_new_password_for_user(user=user, password=new_password)
        return Response({"detail": "Password was successfully updated"}, status=200)
