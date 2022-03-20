from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from open_schools_platform.api.pagination import get_paginated_response, LimitOffsetPagination

from open_schools_platform.users.selectors import user_list, get_user_by_phone, get_token_by_phone, get_token_by_id
from open_schools_platform.users.models import User


# TODO: When JWT is resolved, add authenticated version
from open_schools_platform.users.serializers import CreationTokenSerializer, UserSerializer, OtpSerializer
from open_schools_platform.users.services import is_token_alive, update_token, create_token, check_otp, create_user


class CreationTokenApi(APIView):
    @swagger_auto_schema(
        operation_description="Send sms to entered phone number and"
                              "return token for creation of user"
                              "or tell that user with such number already exist",
        request_body=CreationTokenSerializer,
        responses={201: "Use old sms, it is still alive", 200: "SMS sent", 409: "user already created", 400: "probably incorrect recaptcha"}
    )
    def post(self, request):
        # Make sure the filters are valid, if passed
        token_ser = CreationTokenSerializer(data=request.data)
        token_ser.is_valid(raise_exception=True)

        user = get_user_by_phone(token_ser.data["phone"])
        if user:
            return Response({"detail": "base user with this phone number has already been created"}, status=409)

        token = get_token_by_phone(token_ser.data["phone"])
        if token and is_token_alive(token):
            return Response({"token": token.token}, status=201)

        token = create_token(token_ser.data)
        if not token:
            return Response({"detail": "An error occurred. Probably you sent incorrect recaptcha"}, status=400)

        return Response({"token": token.token}, status=200)


class UserApi(APIView):
    @swagger_auto_schema(
        operation_description="Create base user if verification code is true",
        request_body=OtpSerializer,
        responses={200: "base user was successfully created", 400: "different errors, see in detail"}
    )
    def post(self, request):
        otp_ser = OtpSerializer(data=request.data)
        otp_ser.is_valid(raise_exception=True)

        token = get_token_by_id(otp_ser.data["token"])
        if not token:
            return Response({"detail": "no such token"}, status=400)

        response = check_otp(token.session, otp_ser.data["otp"])
        if response.status_code != 200:
            return Response({"detail": "otp is incorrect"}, status=400)

        user = create_user(token.phone)

        return Response({"user": UserSerializer(user).data}, status=200)
