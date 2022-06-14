from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.compat import set_cookie_with_token
from rest_framework_jwt.settings import api_settings

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import get_dict_from_response
from open_schools_platform.errors.services import AuthFailedException, NotAcceptableException, \
    NotFoundedException, TimeoutErrorException, ValidationErrorException, PermissionDeniedException
from open_schools_platform.user_management.users.selectors import get_user, get_token
from open_schools_platform.api.swagger_tags import SwaggerTags

# TODO: When JWT is resolved, add authenticated version
from open_schools_platform.user_management.users.serializers \
    import CreationTokenSerializer, UserRegisterSerializer, OtpSerializer, \
    RetrieveCreationTokenSerializer, ResendSerializer, UserUpdateSerializer, PasswordUpdateSerializer
from open_schools_platform.user_management.users.services import is_token_alive, create_token, create_user, \
    verify_token, \
    get_jwt_token, update_token_session, set_new_password_for_user
from open_schools_platform.utils.firebase_requests import send_firebase_sms, check_otp


class CreationTokenApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Send sms to entered phone number and"
                              "return token for creation of user"
                              "or tell that user with such number already exist",
        request_body=CreationTokenSerializer,
        responses={201: "Use old sms, it is still alive", 202: "SMS sent", 409: "user already created",
                   400: "probably incorrect recaptcha"},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request):
        # Make sure the filters are valid, if passed
        token_serializer = CreationTokenSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)

        user = get_user(filters=token_serializer.validated_data)
        if user:
            raise AuthFailedException(status=409, detail="user with this phone number has already been created")

        token = get_token(filters=token_serializer.validated_data)
        if token and is_token_alive(token):
            return Response({"token": token.key}, status=201)

        response = send_firebase_sms(**token_serializer.data)

        if response.status_code != 200:
            raise NotAcceptableException(status=400, detail="An error occurred. Probably you sent incorrect recaptcha")

        token = create_token(token_serializer.validated_data["phone"], get_dict_from_response(response)["sessionInfo"])

        return Response({"token": token.key}, status=201)


class RetrieveCreationTokenApi(APIView):
    @swagger_auto_schema(
        operation_description="Return CreationToken data",
        responses={400: "Probably incorrect token", 200: RetrieveCreationTokenSerializer()},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def get(self, request, pk):
        token = get_token(filters={"key": pk})
        if not token:
            raise ValidationErrorException(status=400, detail="Token with such id is not exist.")

        return Response(RetrieveCreationTokenSerializer(token).data)


class UserApi(CreateAPIView):
    @swagger_auto_schema(
        operation_description="Create user due to token",
        request_body=UserRegisterSerializer,
        responses={201: "user was successfully created", 400: "different errors, see in detail"},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request, *args, **kwargs):
        user_serializer = UserRegisterSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        token = get_token(filters=request.data)
        if not token:
            raise NotFoundedException(status=404, detail="no such token")
        if not is_token_alive(token):
            raise NotAcceptableException(status=408, detail="token is overdue")
        if not token.is_verified:
            raise AuthFailedException(status=401, detail="your phone number is not verified", )
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
        operation_description="Create user if verification code is true",
        request_body=OtpSerializer,
        responses={201: "user was successfully created", 400: "different errors, see in detail"},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def put(self, request, pk):
        otp_serializer = OtpSerializer(data=request.data)
        otp_serializer.is_valid(raise_exception=True)

        token = get_token(filters={"key": pk})
        if not token:
            raise NotFoundedException(status=404, detail="no such token")
        if not is_token_alive(token):
            raise NotAcceptableException(status=408, detail="token is overdue")

        response = check_otp(token.session, otp_serializer.validated_data["otp"])
        if response.status_code != 200:
            raise NotAcceptableException(status=400, detail="otp is incorrect")

        verify_token(token)

        return Response({"detail": "token verified"}, status=200)


class CodeResendApi(APIView):
    @swagger_auto_schema(
        operation_description="Resend sms to entered phone number"
                              "or tell that user with such number already exist",
        request_body=ResendSerializer,
        responses={202: "SMS was resent", 409: "user already created", 404: "no such token", 408: "token is overdue"},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def post(self, request, pk):
        recaptcha_serializer = ResendSerializer(data=request.data)
        recaptcha_serializer.is_valid(raise_exception=True)
        token = get_token(filters={"key": pk})

        if not token:
            raise NotFoundedException(status=404, detail="No such token")
        if not is_token_alive(token):
            raise NotAcceptableException(status=408, detail="Token is overdue")

        user = get_user(filters={"phone": token.phone})

        if user:
            raise AuthFailedException(status=409, detail="User with this phone number has already been created")

        sms_response = send_firebase_sms(str(token.phone), recaptcha_serializer.data["recaptcha"])

        if sms_response.status_code == 200:
            update_token_session(token, get_dict_from_response(sms_response)["sessionInfo"])
            return Response({"detail": "SMS was resent"}, status=202)
        else:
            raise TimeoutErrorException(status=400, detail="An error occurred. SMS was not resent")


class UserUpdateApi(ApiAuthMixin, APIView):

    @swagger_auto_schema(
        tags=[SwaggerTags.USER_MANAGEMENT_USERS],
        request_body=UserUpdateSerializer
    )
    def put(self, request, pk):
        user = get_user(filters={"id": pk})
        user_serializer = UserUpdateSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        if request.user == user:
            model_update(instance=user, fields=["name"], data=user_serializer.validated_data)
            return Response({"detail": "User was successfully updated"}, status=200)
        else:
            raise PermissionDeniedException


class UpdatePasswordApi(ApiAuthMixin, APIView):
    @swagger_auto_schema(
        operation_description="Update user password",
        request_body=PasswordUpdateSerializer,
        responses={200: "Password was successfully updated"},
        tags=[SwaggerTags.USER_MANAGEMENT_USERS]
    )
    def put(self, request, pk):
        user = get_user(filters={"id": pk})
        user_serializer = PasswordUpdateSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        old_password = user_serializer.validated_data['old_password']
        new_password = user_serializer.validated_data['new_password']

        if request.user == user and user.check_password(old_password):
            if old_password == new_password:
                raise NotAcceptableException
            set_new_password_for_user(user=user, password=new_password)
            return Response({"detail": "Password was successfully updated"}, status=200)
        else:
            raise PermissionDeniedException

