from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics

from auth_manager.serializers import CreateUserProfileSerializer
from services import auth_services


class UserProfileCreateView(generics.CreateAPIView):

    @swagger_auto_schema(
        operation_description="Create new unverified userprofile or"
                              " responde that such user is already exists",
        request_body=CreateUserProfileSerializer,
        responses={201: "SMS sent", 202: "SMS sent", 409: "already created"}
    )
    def post(self, request, *args, **kwargs):
        user_profile_serializer = CreateUserProfileSerializer(data=request.data)
        user_profile_serializer.is_valid(raise_exception=True)

        reg_user = auth_services.get_userprofile_by_phone_number(
            user_profile_serializer.initial_data["phone_number"]
        )

        if len(reg_user) != 0:
            user_profile = reg_user.get()
            if user_profile.is_verified:
                return Response({"detail": "user with this phone number has already been created"}, status=409)
            else:
                session = auth_services.send_sms(user_profile.phone_number,
                                   user_profile_serializer.initial_data["recaptcha"])
                auth_services.edit_verification_session(user_profile, session)

                return Response(
                    {"detail": "user with this phone number has already been created but not verified, SMS sent"},
                    status=202)
        else:
            user_profile = auth_services.create_unverified_user_profile(
                user_profile_serializer.initial_data["phone_number"]
            )

            session = auth_services.send_sms(user_profile.phone_number,
                                             user_profile_serializer.initial_data["recaptcha"])
            auth_services.create_verification_session(user_profile, session)

            return Response({"detail": "successfully created unverified user, SMS sent"}, status=201)


class VerifyProfileView(generics.CreateAPIView):

    @swagger_auto_schema(
        operation_description="Verify user with given phone by otp",
        request_body=CreateUserProfileSerializer,
        responses={201: "SMS sent", 202: "SMS sent", 409: "already created"}
    )
    def post(self, request, *args, **kwargs):
        user_profile_serializer = CreateUserProfileSerializer(data=request.data)
        user_profile_serializer.is_valid(raise_exception=True)

        reg_user = auth_services.get_userprofile_by_phone_number(
            user_profile_serializer.initial_data["phone_number"]
        )

        if len(reg_user) != 0:
            user_profile = reg_user.get()
            if user_profile.is_verified:
                return Response({"detail": "user with this phone number has already been verified"}, status=409)
            else:
                verification_session = auth_services.get_verification_session(user_profile)
                if not auth_services.is_session_alive(verification_session.creation_date):
                    return Response({"detail": "verification code is overdue"}, status=409)

                firebase_response = auth_services.verify_by_session_and_otp(
                    verification_session.session, user_profile_serializer.initial_data["otp"])

                if firebase_response.status_code == 400:
                    return Response({"detail": "invalid verification code"}, status=400)

                auth_services.verify_user(user_profile)
                return Response({"detail": "successfully verified"}, status=202)
        else:
            return Response({"detail": "user with such telephone number does not exist"}, status=400)
