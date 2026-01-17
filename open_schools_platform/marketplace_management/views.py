import jsonschema
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.paginators import DefaultListPagination
from open_schools_platform.errors.exceptions import AlreadyExists, InvalidArgument
from open_schools_platform.marketplace_management.enums import ManifestFields
from open_schools_platform.marketplace_management.filters import (
    AppFilterset,
    InstallationFilterset,
)
from open_schools_platform.marketplace_management.internal_modules.errors import (
    InternalModuleInitError,
)
from open_schools_platform.marketplace_management.internal_modules.factories import (
    make_module_manager,
)
from open_schools_platform.marketplace_management.models import (
    App,
    Installation,
    AppType,
    AppStatus,
    AppRelease,
    Review,
    InstallationStatus,
)
from open_schools_platform.marketplace_management.serializers import (
    AppSerializer,
    InstallationCreateSerializer,
    InstallationSerializer,
    InstallationStatusUpdateSerializer,
    ReviewCreateSerializer,
    ReviewListSerializer,
    InstallationListSerializer,
    BaseReviewCreateSerializer,
)
from open_schools_platform.marketplace_management.services.installation_status import (
    InstallationStatusService,
)
from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.user_management.users.models import User


# Create your views here.


class AppReviewViewSet(ApiAuthMixin, ModelViewSet):
    serializer_class = ReviewCreateSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        return Review.objects.filter(app_id=self.kwargs["app_id"])

    def get_serializer_class(self):
        if self.action == "create":
            return BaseReviewCreateSerializer
        return ReviewListSerializer

    @swagger_auto_schema(
        operation_description="Create a new review.",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def create(self, request, app_id=None):
        app = get_object_or_404(App, id=app_id)

        if not Installation.objects.filter(
            app=app,
            user=request.user,
            active=True,
        ).exists():
            raise PermissionDenied("You must install app before reviewing")

        data = request.data
        data["app"] = app.id
        serializer = ReviewCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        review = serializer.save(
            user=request.user,
            app=app,
        )

        return Response(
            {
                "id": review.id,
                "rating": review.rating,
                "message": review.message,
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get apps reviews",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AppApi(ApiAuthMixin, ModelViewSet):
    queryset = App.objects.all()
    filterset_class = AppFilterset
    pagination_class = DefaultListPagination
    serializer_class = AppSerializer

    def get_queryset(self):
        return App.objects.annotate(avg_rating=Avg("reviews__rating"))

    @swagger_auto_schema(
        operation_description="Get apps list",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get app",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class InstallationsViewSet(ApiAuthMixin, ModelViewSet):
    queryset = Installation.objects.select_related("organization", "app")
    serializer_class = InstallationSerializer
    pagination_class = DefaultListPagination
    filterset_class = InstallationFilterset

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

        if user == installation.user:
            return True

        if getattr(user, "is_admin", False):
            return True

        return False

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

    def get_queryset(self):
        user: User = self.request.user  # noqa
        qs = super().get_queryset()
        if not user.is_authenticated:
            return qs
        return qs.filter(
            organization_id__in=user.employee_profile.employees.values_list(
                "organization_id"
            )
        )

    @swagger_auto_schema(
        operation_description="Create new installation",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Installation.objects.filter(
            app_id=serializer.validated_data["app"].id,
            organization_id=serializer.validated_data["organization"].id,
        ).exists():
            raise AlreadyExists("This app already installed for that organization")

        app = App.objects.get(id=serializer.validated_data["app"].id)
        if not (app.type == AppType.INTERNAL and app.status == AppStatus.PUBLISHED):
            raise InvalidArgument("App with such id don't available now")

        user_organization_employee: Employee = (
            self.request.user.employee_profile.employees.filter(
                organization_id=serializer.validated_data["organization"].id
            ).first()
        )

        if (
            self.request.user.is_authenticated is False
            or user_organization_employee is None
        ):
            raise PermissionDenied(
                "Only organization employees can perform this action."
            )

        latest_app_release: AppRelease = app.latest_release
        if latest_app_release is None:
            raise NotFound("No app release available")

        config_schema = latest_app_release.manifest.get(
            ManifestFields.config_schema.value
        )
        if config_schema is not None:
            try:
                jsonschema.validate(
                    instance=serializer.validated_data["config_data"],
                    schema=config_schema,
                )
            except jsonschema.exceptions.ValidationError:
                raise InvalidArgument("Invalid config_data")

        app_entry = latest_app_release.manifest.get(ManifestFields.entry.value)

        module_manager = make_module_manager()
        try:
            module_manager.initialize(
                app_id=serializer.validated_data["app"].id,
                org_id=serializer.validated_data["organization"].id,
                config_data=serializer.validated_data["config_data"],
            )
        except InternalModuleInitError:
            # TODO We should use installation lifecycle statuses and log error
            installation = serializer.save(
                status=InstallationStatus.STATUS_DISABLED,
                installed_at=None,
                user=request.user,
            )
        else:
            installation = serializer.save(
                status=InstallationStatus.STATUS_ACTIVE,
                installed_at=timezone.now(),
                user=request.user,
            )
        return Response(
            {
                "id": installation.id,
                "app_id": installation.app_id,
                "organization_id": installation.organization_id,
                "status": "active" if installation.active else "disabled",
                "config_data": installation.config_data,
                "app_entry": app_entry,
            },
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description="Get installation details",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete installation",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        responses={
            204: "Installation deleted successfully",
            404: "Installation not found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Delete installation (стандартная реализация DRF)"""
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get installations list",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AdminInstallationViewSet(ApiAuthMixin, ModelViewSet):
    """
    ViewSet for the administrative settings API
    """

    queryset = Installation.objects.select_related("app", "organization").all()
    filterset_class = InstallationFilterset
    pagination_class = DefaultListPagination
    serializer_class = InstallationListSerializer

    @swagger_auto_schema(
        operation_description="Get a list of installations filtered by school, app, and status",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        responses={200: InstallationListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
