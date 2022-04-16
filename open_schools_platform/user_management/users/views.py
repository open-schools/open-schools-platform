from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.compat import set_cookie_with_token
from rest_framework_jwt.settings import api_settings

from open_schools_platform.user_management.users.selectors import get_user, get_token

# TODO: When JWT is resolved, add authenticated version
from open_schools_platform.user_management.users.serializers \
    import CreationTokenSerializer, UserRegisterSerializer, OtpSerializer
from open_schools_platform.user_management.users.services import is_token_alive, create_token, check_otp, create_user, \
    verify_token, \
    get_jwt_token


class CreationTokenApi(APIView):
    @swagger_auto_schema(
        operation_description="Send sms to entered phone number and"
                              "return token for creation of user"
                              "or tell that user with such number already exist",
        request_body=CreationTokenSerializer,
        responses={201: "Use old sms, it is still alive", 200: "SMS sent", 409: "user already created",
                   400: "probably incorrect recaptcha"}
    )
    def post(self, request):
        # Make sure the filters are valid, if passed
        token_ser = CreationTokenSerializer(data=request.data)
        token_ser.is_valid(raise_exception=True)

        user = get_user(filters=token_ser.validated_data)
        if user:
            return Response({"detail": "user with this phone number has already been created"}, status=409)

        token = get_token(filters=token_ser.validated_data)
        if token and is_token_alive(token):
            return Response({"token": token.key}, status=201)

        token = create_token(**token_ser.data)
        if not token:
            return Response({"detail": "An error occurred. Probably you sent incorrect recaptcha"}, status=400)

        return Response({"token": token.key}, status=200)


class UserApi(APIView):
    @swagger_auto_schema(
        operation_description="Create user due to token",
        request_body=UserRegisterSerializer,
        responses={200: "user was successfully created", 400: "different errors, see in detail"}
    )
    def post(self, request, *args, **kwargs):
        user_ser = UserRegisterSerializer(data=request.data)
        user_ser.is_valid(raise_exception=True)

        token = get_token(filters=request.data)
        if not token:
            return Response({"detail": "no such token"}, status=400)
        if not is_token_alive(token):
            return Response({"detail": "token is overdue"}, status=400)
        if not token.is_verified:
            return Response({"detail": "your phone number is not verified"}, status=400)

        user = create_user(
            phone=token.phone,
            name=user_ser.data["name"],
            password=user_ser.data["password"]
        )
        if not user:
            return Response({"detail": "error when creating user"}, status=400)

        token = get_jwt_token(user.USERNAME_FIELD, str(user.get_username()),
                              user_ser.data["password"], request)

        response = Response({"token": token}, status=status.HTTP_201_CREATED)
        if api_settings.JWT_AUTH_COOKIE:
            set_cookie_with_token(response, api_settings.JWT_AUTH_COOKIE, token)

        return response


class VerificationApi(APIView):
    @swagger_auto_schema(
        operation_description="Create user if verification code is true",
        request_body=OtpSerializer,
        responses={200: "user was successfully created", 400: "different errors, see in detail"}
    )
    def post(self, request):
        otp_ser = OtpSerializer(data=request.data)
        otp_ser.is_valid(raise_exception=True)

        token = get_token(filters=otp_ser.data)
        if not token:
            return Response({"detail": "no such token"}, status=400)
        if not is_token_alive(token):
            return Response({"detail": "token is overdue"}, status=400)

        response = check_otp(token.session, otp_ser.data["otp"])
        if response.status_code != 200:
            return Response({"detail": "otp is incorrect"}, status=400)

        verify_token(token)

        return Response({"detail": "token verified"}, status=200)
