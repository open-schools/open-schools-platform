from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, AuthenticationFailed, APIException, \
    ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.compat import set_cookie_with_token
from rest_framework_jwt.settings import api_settings

from open_schools_platform.common.utils import get_dict_from_response
from open_schools_platform.errors.services import InvalidArgumentException
from open_schools_platform.user_management.users.selectors import get_user, get_token
from open_schools_platform.api.swagger_tags import SwaggerTags

# TODO: When JWT is resolved, add authenticated version
from open_schools_platform.user_management.users.serializers \
    import CreationTokenSerializer, UserRegisterSerializer, OtpSerializer, \
    RetrieveCreationTokenSerializer, ResendSerializer, \
    PasswordResetSerializer
from open_schools_platform.user_management.users.services import is_token_alive, create_token, create_user, \
    verify_token, \
    get_jwt_token, update_token_session, set_new_password_for_user
from open_schools_platform.utils.firebase_requests import send_firebase_sms, check_otp


class CreationTokenApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Send sms to entered phone number and"
                              "return token for phone verification. Creation token id as a response.",
        request_body=CreationTokenSerializer,
        responses={200: "Use old sms, it is still alive.", 201: "Token created and SMS was sent.",
                   422: "probably incorrect recaptcha."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request):
        token_serializer = CreationTokenSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)

        token = get_token(filters=token_serializer.validated_data)
        if token and is_token_alive(token):
            return Response({"token": token.key}, status=200)

        response = send_firebase_sms(**token_serializer.data)

        if response.status_code != 200:
            raise InvalidArgumentException(detail="An error occurred. Probably you sent incorrect recaptcha.")

        token = create_token(token_serializer.validated_data["phone"], get_dict_from_response(response)["sessionInfo"])

        return Response({"token": token.key}, status=201)


class RetrieveCreationTokenApi(APIView):
    @swagger_auto_schema(
        operation_description="Return CreationToken data.",
        responses={400: "Probably incorrect token", 200: RetrieveCreationTokenSerializer()},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def get(self, request, pk):
        token = get_token(filters={"key": pk})
        if not token:
            raise ValidationError(detail="Token with such id is not exist.")

        return Response(RetrieveCreationTokenSerializer(token).data)


class UserApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create user due to verificated token.",
        request_body=UserRegisterSerializer,
        responses={201: "User was successfully created. JWT token as a response."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request, *args, **kwargs):
        user_serializer = UserRegisterSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        token = get_token(filters=request.data)
        if not token:
            raise NotFound(detail="No such token.")
        if not is_token_alive(token):
            raise AuthenticationFailed(detail="Token is overdue.")
        if not token.is_verified:
            raise AuthenticationFailed(detail="Your phone number is not verified.")
        user = create_user(
            phone=token.phone,
            name=user_serializer.data["name"],
            password=user_serializer.data["password"]
        )
        token = get_jwt_token(user.USERNAME_FIELD, str(user.get_username()),
                              user_serializer.data["password"], request)

        response = Response({"token": token}, status=status.HTTP_201_CREATED)
        if api_settings.JWT_AUTH_COOKIE:
            set_cookie_with_token(response, api_settings.JWT_AUTH_COOKIE, token)

        return response


class VerificationApi(APIView):
    @swagger_auto_schema(
        operation_description="Verify phone number with CreationToken if otp is correct.",
        request_body=OtpSerializer,
        responses={200: "Phone number verified.", 422: "Incorrect otp."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def put(self, request, pk):
        otp_serializer = OtpSerializer(data=request.data)
        otp_serializer.is_valid(raise_exception=True)

        token = get_token(filters={"key": pk})
        if not token:
            raise NotFound(detail="No such token.")
        if not is_token_alive(token):
            raise AuthenticationFailed(detail="Token is overdue.")

        response = check_otp(token.session, otp_serializer.validated_data["otp"])
        if response.status_code != 200:
            raise InvalidArgumentException(detail="Otp is incorrect.")

        verify_token(token)

        return Response({"detail": "Token verified."}, status=200)


class CodeResendApi(APIView):
    @swagger_auto_schema(
        operation_description="Resend sms to entered phone number"
                              "or tell that user with such number already exist.",
        request_body=ResendSerializer,
        responses={200: "SMS was resent."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request, pk):
        recaptcha_serializer = ResendSerializer(data=request.data)
        recaptcha_serializer.is_valid(raise_exception=True)
        token = get_token(filters={"key": pk})

        if not token:
            raise NotFound(detail="No such token.")
        if not is_token_alive(token):
            raise AuthenticationFailed(detail="Token is overdue.")

        user = get_user(filters={"phone": token.phone})

        if user:
            raise AuthenticationFailed(detail="User with this phone number has already been created.")

        sms_response = send_firebase_sms(str(token.phone), recaptcha_serializer.data["recaptcha"])

        if sms_response.status_code != 200:
            raise APIException(detail="An error occurred. SMS was not resent.")

        update_token_session(token, get_dict_from_response(sms_response)["sessionInfo"])
        return Response({"detail": "SMS was resent"}, status=200)


class UserResetPasswordApi(APIView):
    @swagger_auto_schema(
        operation_description="Reset user's password",
        tags=[SwaggerTags.USER_MANAGEMENT_USERS],
        request_body=PasswordResetSerializer,
        responses={200: "Password was successfully reset"},
    )
    def post(self, request):
        user_serializer = PasswordResetSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        token = get_token(filters={"key": user_serializer.validated_data['token']})
        if not token:
            raise NotFound(detail="No such token")
        user = get_user(filters={"phone": token.phone})
        if not user:
            raise NotFound(detail="No such user")
        if not token.is_verified:
            raise AuthenticationFailed(detail="Token is not verified")
        if not is_token_alive(token):
            raise AuthenticationFailed(detail="Token is overdue")

        set_new_password_for_user(user=user, password=user_serializer.validated_data['password'])
        return Response({"detail": "Password was successfully reset"}, status=200)
