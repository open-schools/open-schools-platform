from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import generics

from auth_manager.serializers import CreateUserProfileSerializer
from auth_manager.utils.sender_sms import send_sms
from services import auth_services


class UserProfileCreateView(generics.CreateAPIView):

    @swagger_auto_schema(
        operation_description="Create new unverified userprofile or"
                              " responde that such user is already exists",
        request_body=CreateUserProfileSerializer,
        responses={201: "SMS sent", 202: "SMS sent", 409: "already created"}
    )
    def post(self, request, *args, **kwargs):
        user_profile_serializer = CreateUserProfileSerializer(
            data={"phone_number": request.data["phone_number"],
                  "recaptcha": request.data["recaptcha"]}
        )
        user_profile_serializer.is_valid(raise_exception=True)
        reg_user = auth_services.get_userprofile_by_phone_number(
            user_profile_serializer.initial_data["phone_number"]
        )

        if len(reg_user) != 0:
            user_profile = reg_user.get()
            if user_profile.is_verified:
                return Response({"detail": "user with this phone number has already been created"}, status=409)
            else:
                session = send_sms(user_profile.phone_number,
                                   user_profile_serializer.initial_data["recaptcha"])
                auth_services.edit_verification_session(user_profile, session)

                return Response(
                    {"detail": "user with this phone number has already been created but not verified, SMS sent"},
                    status=202)
        else:
            user_profile = auth_services.create_unverified_user_profile(
                user_profile_serializer.initial_data["phone_number"]
            )

            session = send_sms(user_profile.phone_number,
                               user_profile_serializer.initial_data["recaptcha"])
            auth_services.create_verification_session(user_profile, session)

            return Response({"detail": "successfully created unverified user, SMS sent"}, status=201)