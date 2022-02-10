from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics

from models.models import UserProfile
from auth_manager.serializers import CreateUserProfileSerializer
from services.auth_manager_services import CreateUnverifiedUserProfile


class UserProfileView(generics.CreateAPIView):

    # @swagger_auto_schema(
    #     method="post",
    #     operation_description="Create and register user with verifying by phone",
    #     request_body=CreateUserProfileSerializer,
    #     responses={201: "SMS sent", 202: "SMS sent", 409: "already created"}
    # )
    # @api_view(["POST"])
    # @permission_classes([AllowAny])
    def post(self, request, *args, **kwargs):
        reg_user = UserProfile.objects.filter(
            phone_number=request.data["phone_number"]
        )

        if len(reg_user) != 0:
            if reg_user.get().is_verified:
                return Response({"detail": "user with this phone number has already been created"}, status=409)
            else:
                return Response(
                    {"detail": "user with this phone number has already been created but not verified, SMS sent"},
                    status=202)
        else:
            userProfileSerializer = CreateUserProfileSerializer(
                data={"phone_number": request.data["phone_number"],
                      "is_verified": False}
            )
            userProfileSerializer.is_valid(raise_exception=True)
            CreateUnverifiedUserProfile(userProfileSerializer)

            # tokens = TokenObtainPairSerializer(data=serializerUser.validated_data)
            # tokens.user = user
            # tokens.is_valid()
            return Response({"detail": "succsessfully create unverified user, SMS sent"}, status=201)
