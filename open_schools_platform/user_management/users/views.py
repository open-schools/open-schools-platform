from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.compat import set_cookie_with_token
from rest_framework_jwt.settings import api_settings

from open_schools_platform.common.utils import get_dict_from_response
from open_schools_platform.errors.services import TriggerAuthFailed, TriggerNotAcceptable, \
    TriggerNotFounded, TriggerTimeoutError
from open_schools_platform.user_management.users.selectors import get_user, get_token

# TODO: When JWT is resolved, add authenticated version
from open_schools_platform.user_management.users.serializers \
    import CreationTokenSerializer, UserRegisterSerializer, OtpSerializer, ResendSerializer, \
    RetrieveCreationTokenSerializer
from open_schools_platform.user_management.users.services import is_token_alive, create_token, create_user, \
    verify_token, \
    get_jwt_token, update_token_session
from open_schools_platform.utils.firebase_requests import send_sms, check_otp


class CreationTokenApi(APIView):
    @swagger_auto_schema(
        operation_description="Return CreationToken data",
        responses={400: "Probably incorrect token", 200: RetrieveCreationTokenSerializer()}
    )
    def get(self, request):
        key = request.GET.get("token", "")
        if key == "":
            raise ValidationError("Enter a valid UUID.")

        return Response(RetrieveCreationTokenSerializer(get_token(filters={"key": key})).data)

    @swagger_auto_schema(
        operation_description="Send sms to entered phone number and"
                              "return token for creation of user"
                              "or tell that user with such number already exist",
        request_body=CreationTokenSerializer,
        responses={201: "Use old sms, it is still alive", 202: "SMS sent", 409: "user already created",
                   400: "probably incorrect recaptcha"}
    )
    def post(self, request):
        # Make sure the filters are valid, if passed
        token_ser = CreationTokenSerializer(data=request.data)
        token_ser.is_valid(raise_exception=True)

        user = get_user(filters=token_ser.validated_data)
        if user:
            raise TriggerAuthFailed(status=409, detail="user with this phone number has already been created")

        token = get_token(filters=token_ser.validated_data)
        if token and is_token_alive(token):
            return Response({"token": token.key}, status=201)

        response = send_sms(**token_ser.data)

        if response.status_code != 200:
            raise TriggerNotAcceptable(status=400, detail="An error occurred. Probably you sent incorrect recaptcha")

        token = create_token(token_ser.validated_data["phone"], get_dict_from_response(response)["sessionInfo"])

        return Response({"token": token.key}, status=201)


class UserApi(APIView):
    @swagger_auto_schema(
        operation_description="Create user due to token",
        request_body=UserRegisterSerializer,
        responses={201: "user was successfully created", 400: "different errors, see in detail"}
    )
    def post(self, request, *args, **kwargs):
        user_ser = UserRegisterSerializer(data=request.data)
        user_ser.is_valid(raise_exception=True)

        token = get_token(filters=request.data)
        if not token:
            raise TriggerNotFounded(status=404, detail="no such token")
        if not is_token_alive(token):
            raise TriggerNotAcceptable(status=408, detail="token is overdue")
        if not token.is_verified:
            raise TriggerAuthFailed(status=401, detail="your phone number is not verified",)
        user = create_user(
            phone=token.phone,
            name=user_ser.data["name"],
            password=user_ser.data["password"]
        )
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
        responses={201: "user was successfully created", 400: "different errors, see in detail"}
    )
    def post(self, request):
        otp_ser = OtpSerializer(data=request.data)
        otp_ser.is_valid(raise_exception=True)

        token = get_token(filters=otp_ser.data)
        if not token:
            raise TriggerNotFounded(status=404, detail="no such token")
        if not is_token_alive(token):
            raise TriggerNotAcceptable(status=408, detail="token is overdue")

        response = check_otp(token.session, otp_ser.data["otp"])
        if response.status_code != 200:
            raise TriggerNotAcceptable(status=400, detail="otp is incorrect")

        verify_token(token)

        return Response({"detail": "token verified"}, status=200)


class CodeResendApi(APIView):
    @swagger_auto_schema(
        operation_description="Resend sms to entered phone number"
                              "or tell that user with such number already exist",
        request_body=ResendSerializer,
        responses={202: "SMS was resent", 409: "user already created", 404: "no such token", 408: "token is overdue"}
    )
    def post(self, request):
        # Make sure the filters are valid, if passed
        token_ser = ResendSerializer(data=request.data)
        token_ser.is_valid(raise_exception=True)

        token = get_token(filters=token_ser.data)

        if not token:
            raise TriggerNotFounded(status=404, detail="no such token")
        if not is_token_alive(token):
            raise TriggerNotAcceptable(status=408, detail="token is overdue")

        user = get_user(filters={"phone": token.phone})

        if user:
            raise TriggerAuthFailed(status=409, detail="user with this phone number has already been created")

        sms_response = send_sms(str(token.phone), token_ser.data["recaptcha"])

        if sms_response.status_code == 200:
            update_token_session(token, get_dict_from_response(sms_response)["sessionInfo"])
            return Response({"detail": "SMS was resent"}, status=202)
        else:
            raise TriggerTimeoutError(status=400, detail="An error occurred. SMS was not resent")
