from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.compat import set_cookie_with_token
from rest_framework_jwt.settings import api_settings

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.common.utils import get_dict_from_response
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.errors.exceptions import InvalidArgumentException
from open_schools_platform.user_management.users.selectors import get_user, get_token, get_token_with_checks
from open_schools_platform.api.swagger_tags import SwaggerTags

# TODO: When JWT is resolved, add authenticated version
from open_schools_platform.user_management.users.serializers \
    import CreationTokenSerializer, UserRegisterSerializer, OtpSerializer, \
    RetrieveCreationTokenSerializer, ResendSerializer, \
    PasswordResetSerializer, FCMNotificationToken
from open_schools_platform.user_management.users.services import is_token_alive, create_token, create_user, \
    verify_token, \
    get_jwt_token, update_token_session, set_new_password_for_user, update_fcm_notification_token_entity
from open_schools_platform.utils.firebase_requests import send_firebase_sms, check_otp_with_firebase, \
    firebase_error_dict_with_additional_info


class CreationTokenApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Send sms to entered phone number and"
                              "return token for phone verification. Creation token id as a response.",
        request_body=CreationTokenSerializer,
        responses={200: "Use old sms, it is still alive. Creation token id as response.",
                   201: "Token created and SMS was sent. Creation token id as response.",
                   400: "Probably incorrect recaptcha.", 401: "Token is not verified or it is overdue.",
                   404: "Such token was not found."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request):
        token_serializer = CreationTokenSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)

        token = get_token(filters=token_serializer.validated_data)
        if token and is_token_alive(token):
            return Response({"token": token.key}, status=200)

        response = send_firebase_sms(**token_serializer.validated_data)

        if response.status_code != 200:
            raise InvalidArgumentException(detail=firebase_error_dict_with_additional_info(response))

        token = create_token(token_serializer.validated_data["phone"], get_dict_from_response(response)["sessionInfo"])

        return Response({"token": token.key}, status=201)


class RetrieveCreationTokenApi(APIView):
    @swagger_auto_schema(
        operation_description="Return CreationToken data.",
        responses={404: "Token with that id was not found.",
                   200: convert_dict_to_serializer({"token": RetrieveCreationTokenSerializer()})},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def get(self, request, pk):
        token = get_token(
            filters={"key": pk},
            empty_exception=True,
        )

        return Response({"token": RetrieveCreationTokenSerializer(token).data}, status=200)


class UserApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create user due to verificated token.",
        request_body=UserRegisterSerializer,
        responses={201: "User was successfully created. JWT token as a response.",
                   401: "Token is not verified or it is overdue.", 404: "Such token was not found."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request, *args, **kwargs):
        user_serializer = UserRegisterSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        token = get_token_with_checks(key=user_serializer.validated_data['token'])

        user = create_user(
            phone=token.phone,
            name=user_serializer.validated_data["name"],
            password=user_serializer.validated_data["password"]
        )
        jwt_token = get_jwt_token(user.USERNAME_FIELD, str(user.get_username()),
                                  user_serializer.validated_data["password"], request)

        response = Response({"token": jwt_token}, status=status.HTTP_201_CREATED)
        if api_settings.JWT_AUTH_COOKIE:
            set_cookie_with_token(response, api_settings.JWT_AUTH_COOKIE, jwt_token)

        return response


class VerificationApi(APIView):
    @swagger_auto_schema(
        operation_description="Verify phone number with CreationToken if otp is correct.",
        request_body=OtpSerializer,
        responses={200: "Phone number verified.", 400: "Incorrect otp.",
                   401: "Token is not verified or it is overdue.", 404: "Such token was not found."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def patch(self, request, pk):
        otp_serializer = OtpSerializer(data=request.data)
        otp_serializer.is_valid(raise_exception=True)

        token = get_token_with_checks(key=pk, verify_check=False)

        response = check_otp_with_firebase(token.session, otp_serializer.validated_data["otp"])
        if response.status_code != 200:
            raise InvalidArgumentException(detail="Otp is incorrect.")

        verify_token(token)

        return Response({"detail": "Token verified."}, status=200)


class CodeResendApi(APIView):
    @swagger_auto_schema(
        operation_description="Resend sms to entered phone number "
                              "or tell that user with such number already exist.",
        request_body=ResendSerializer,
        responses={200: "SMS was resent.", 400: "Probably incorrect recaptcha.",
                   401: "Token is not verified or it is overdue.",
                   404: "Such token was not found."},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request, pk):
        recaptcha_serializer = ResendSerializer(data=request.data)
        recaptcha_serializer.is_valid(raise_exception=True)

        token = get_token_with_checks(key=pk, verify_check=False)

        response = send_firebase_sms(str(token.phone), recaptcha_serializer.validated_data["recaptcha"])

        if response.status_code != 200:
            raise InvalidArgumentException(detail=firebase_error_dict_with_additional_info(response))

        update_token_session(token, get_dict_from_response(response)["sessionInfo"])
        return Response({"detail": "SMS was resent."}, status=200)


class UserResetPasswordApi(APIView):
    @swagger_auto_schema(
        operation_description="Reset user's password.",
        tags=[SwaggerTags.USER_MANAGEMENT_USERS],
        request_body=PasswordResetSerializer,
        responses={200: "Password was successfully reset.", 401: "Token is not verified or it is overdue.",
                   404: "Such token or user were not found."},
    )
    def post(self, request):
        user_serializer = PasswordResetSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        token = get_token_with_checks(key=user_serializer.validated_data['token'])

        user = get_user(
            filters={"phone": token.phone},
            empty_exception=True,
            empty_message="No user with such phone"
        )

        set_new_password_for_user(user=user, password=user_serializer.validated_data['password'])
        return Response({"detail": "Password was successfully reset."}, status=200)


class AddFCMNotificationTokenApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Add FCM notification token to request user.",
        tags=[SwaggerTags.USER_MANAGEMENT_USERS],
        request_body=FCMNotificationToken,
        responses={200: "FCM notification token was successfully added."},
    )
    def patch(self, request):
        token_serializer = FCMNotificationToken(data=request.data)
        token_serializer.is_valid(raise_exception=True)
        update_fcm_notification_token_entity(token=request.user.firebase_token, data=token_serializer.validated_data)
        return Response({"detail": "FCM notification token was successfully added."}, status=200)
