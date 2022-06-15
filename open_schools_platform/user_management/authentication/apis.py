from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import JSONWebTokenWithTwoResponses

from rest_framework_jwt.views import BaseJSONWebTokenAPIView

from open_schools_platform.api.mixins import ApiAuthMixin

from open_schools_platform.user_management.authentication.services import auth_logout


from open_schools_platform.api.swagger_tags import SwaggerTags
from ..users.serializers import UserSerializer


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
        tags=[SwaggerTags.USER_MANAGEMENT_AUTH],
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response({"user": UserSerializer(request.user).data},
                        status=200)
