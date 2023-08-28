from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import JSONWebTokenWithTwoResponses, UpdatePasswordSerializer, UpdateUserSerializer

from rest_framework_jwt.views import BaseJSONWebTokenAPIView

from open_schools_platform.api.mixins import ApiAuthMixin

from open_schools_platform.user_management.authentication.services import auth_logout

from open_schools_platform.api.swagger_tags import SwaggerTags
from ..users.serializers import GetUserSerializer, GetUserProfilesSerializer
from ..users.services import set_new_password_for_user, user_update
from ...common.views import convert_dict_to_serializer


class UserJwtLoginApi(BaseJSONWebTokenAPIView):
    serializer_class = JSONWebTokenWithTwoResponses
    throttle_scope = "login"

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
        responses={200: convert_dict_to_serializer({"user": GetUserProfilesSerializer()})},
    )
    def get(self, request):
        return Response({"user": GetUserProfilesSerializer(request.user, context={'request': request}).data},
                        status=200)

    @swagger_auto_schema(
        operation_description="Update user.",
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH],
        request_body=UpdateUserSerializer,
        responses={200: convert_dict_to_serializer({"user": GetUserSerializer()})}
    )
    def patch(self, request):
        user = request.user
        user_serializer = UpdateUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_update(user=user, data=user_serializer.validated_data)
        return Response({"user": GetUserSerializer(user).data}, status=200)


class UpdatePasswordApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Update user password.",
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH],
        request_body=UpdatePasswordSerializer,
        responses={200: "Password was successfully updated."},
    )
    def patch(self, request):
        user_serializer = UpdatePasswordSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = request.user

        old_password = user_serializer.validated_data['old_password']
        new_password = user_serializer.validated_data['new_password']

        if not user.check_password(old_password):
            raise AuthenticationFailed(detail="Old password does not match with actual one.")
        if old_password == new_password:
            raise AuthenticationFailed(detail="New password matches with the old one.")

        set_new_password_for_user(user=user, password=new_password)
        return Response({"detail": "Password was successfully updated"}, status=200)
