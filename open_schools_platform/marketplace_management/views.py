from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.paginators import DefaultListPagination
from open_schools_platform.marketplace_management.filters import AppFilterset
from open_schools_platform.marketplace_management.models import App, Installation
from open_schools_platform.marketplace_management.serializers import AppSerializer, InstallationCreateSerializer, \
    InstallationSerializer


# Create your views here.

class AppApi(ApiAuthMixin, ModelViewSet):
    queryset = App.objects.all()
    filterset_class = AppFilterset
    pagination_class = DefaultListPagination
    serializer_class = AppSerializer

    @swagger_auto_schema(
        operation_description="Get apps list",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class InstallationsViewSet(ModelViewSet):
    serializer_class = InstallationSerializer
    queryset = Installation.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return InstallationCreateSerializer
        return self.serializer_class

    @swagger_auto_schema(
        operation_description="Get apps list",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def create(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get apps list",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def retrieve(self, *args, **kwargs):
        return super().list(*args, **kwargs)
