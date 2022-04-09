from djoser.serializers import UserCreateSerializer
from djoser.views import TokenCreateView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenViewBase

from registration.serializers import CreateUserProfileSerializer


class UserProfileCreateView(generics.CreateAPIView):


    def post(self, request, *args, **kwargs):
        serializerUser = UserCreateSerializer(data={"username": request.data["phone_number"],
                                          "password": request.data["password"]})

        userProfileSerializer = CreateUserProfileSerializer(data=request.data)

        serializerUser.is_valid(raise_exception=True)
        userProfileSerializer.is_valid(raise_exception=True)
        user = serializerUser.create(serializerUser.validated_data)
        userProfile = userProfileSerializer.create(userProfileSerializer.validated_data)

        userProfile.user = user
        user.save()
        userProfile.save()

        tokens = TokenObtainPairSerializer(data=serializerUser.validated_data)
        tokens.user = user
        tokens.is_valid()

        return Response(tokens.validated_data, status=200)