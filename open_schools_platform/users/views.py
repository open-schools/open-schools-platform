from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.users.selectors import get_user_by_phone, get_token_by_phone, get_token_by_id

# TODO: When JWT is resolved, add authenticated version
from open_schools_platform.users.serializers import CreationTokenSerializer, UserRegisterSerializer, OtpSerializer, \
    UserSerializer
from open_schools_platform.users.services import is_token_alive, create_token, check_otp, create_user, verify_token


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

        user = get_user_by_phone(token_ser.data["phone"])
        if user:
            return Response({"detail": "user with this phone number has already been created"}, status=409)

        token = get_token_by_phone(token_ser.data["phone"])
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
    def post(self, request):
        token_str = request.data.get("token")

        user_ser = UserRegisterSerializer(data=request.data)
        user_ser.is_valid(raise_exception=True)

        token = get_token_by_id(token_str)
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

        return Response({"user": UserSerializer(user).data}, status=200)


class VerificationApi(APIView):
    @swagger_auto_schema(
        operation_description="Create user if verification code is true",
        request_body=OtpSerializer,
        responses={200: "user was successfully created", 400: "different errors, see in detail"}
    )
    def post(self, request):
        otp_ser = OtpSerializer(data=request.data)
        otp_ser.is_valid(raise_exception=True)

        token = get_token_by_id(otp_ser.data["token"])
        if not token:
            return Response({"detail": "no such token"}, status=400)
        if not is_token_alive(token):
            return Response({"detail": "token is overdue"}, status=400)

        response = check_otp(token.session, otp_ser.data["otp"])
        if response.status_code != 200:
            return Response({"detail": "otp is incorrect"}, status=400)

        verify_token(token)

        return Response({"detail": "token verified"}, status=200)