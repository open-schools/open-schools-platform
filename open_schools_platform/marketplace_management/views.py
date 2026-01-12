from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.paginators import DefaultListPagination
from open_schools_platform.marketplace_management.filters import AppFilterset, InstallationFilterset
from open_schools_platform.marketplace_management.models import App, Installation
from open_schools_platform.marketplace_management.serializers import (
    AppSerializer,
    InstallationCreateSerializer,
    InstallationSerializer,
    InstallationListSerializer,
    InstallationStatusUpdateSerializer,
)
from open_schools_platform.marketplace_management.services.installation_status import (
    InstallationStatusService,
)


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


class InstallationsViewSet(ApiAuthMixin, ModelViewSet):
    queryset = Installation.objects.select_related("organization", "app")
    serializer_class = InstallationSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return InstallationCreateSerializer
        if self.action == "change_status":
            return InstallationStatusUpdateSerializer
        return InstallationSerializer

    @staticmethod
    def _can_manage_installation(user, installation) -> bool:
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_admin", False):
            return True

        organization = installation.organization

        return organization.teachers.filter(
            teacher_profile__user_id=user.id
        ).exists()

    @swagger_auto_schema(
        operation_description="Install app to organization",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get installation by id",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # PATCH /installations/{id}/status
    @action(detail=True, methods=["patch"], url_path="status")
    @swagger_auto_schema(
        operation_description="Change installation status",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        request_body=InstallationStatusUpdateSerializer,
        responses={200: InstallationSerializer},
    )
    def change_status(self, request, pk=None):
        installation = self.get_object()

        if not self._can_manage_installation(request.user, installation):
            return Response(
                {"detail": "No rights to manage the organization"},
                status=403,
            )

        serializer = InstallationStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        InstallationStatusService.change_status(
            installation=installation,
            new_status=serializer.validated_data["status"],
            user=request.user,
        )

        return Response(InstallationSerializer(installation).data)


class AdminInstallationViewSet(ApiAuthMixin, ModelViewSet):
    """
    ViewSet for the administrative settings API
    """
    queryset = Installation.objects.select_related('app', 'organization').all()
    filterset_class = InstallationFilterset
    pagination_class = DefaultListPagination
    serializer_class = InstallationListSerializer

    @swagger_auto_schema(
        operation_description="Get a list of installations filtered by school, app, and status",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        responses={200: InstallationListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
