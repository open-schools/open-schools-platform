import jsonschema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.paginators import DefaultListPagination
from open_schools_platform.errors.exceptions import AlreadyExists, InvalidArgument
from open_schools_platform.marketplace_management.filters import (
    AppFilterset,
    InstallationFilterset,
)
from open_schools_platform.marketplace_management.models import (
    App,
    Installation,
    AppStatus,
    Review,
)
from open_schools_platform.marketplace_management.serializers import (
    AppSerializer,
    InstallationCreateSerializer,
    InstallationSerializer,
    InstallationListSerializer,
    ReviewSerializer,
    ReviewCreateSerializer,
)
from open_schools_platform.organization_management.employees.models import Employee


class AppApi(ApiAuthMixin, ModelViewSet):
    queryset = App.objects.filter(status=AppStatus.PUBLISHED)
    filterset_class = AppFilterset
    pagination_class = DefaultListPagination
    serializer_class = AppSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return App.objects.all()
        return App.objects.filter(status=AppStatus.PUBLISHED)

    @swagger_auto_schema(
        operation_description="Get apps list",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get app details",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ReviewApi(ApiAuthMixin, ModelViewSet):
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        app_id = self.kwargs.get("app_id")
        return Review.objects.filter(app_id=app_id).order_by("-created_at")

    @swagger_auto_schema(
        operation_description="Get app reviews list",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create app review",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        app_id = self.kwargs.get("app_id")
        user = self.request.user
        
        has_installed = Installation.objects.filter(app_id=app_id, user=user).exists()
        if not has_installed:
            raise PermissionDenied("You must install the app before leaving a review.")

        if Review.objects.filter(app_id=app_id, user=user).exists():
            raise AlreadyExists("You have already reviewed this app.")

        serializer.save(app_id=app_id, user=user)
        
        app = App.objects.get(id=app_id)
        from django.db.models import Avg
        agg = Review.objects.filter(app_id=app_id).aggregate(Avg('rating'))
        app.average_rating = agg['rating__avg'] or 0.0
        app.reviews_count = Review.objects.filter(app_id=app_id).count()
        app.save()



class InstallationsViewSet(ApiAuthMixin, ModelViewSet):
    serializer_class = InstallationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return Installation.objects.all()
        if not user.is_authenticated:
            return Installation.objects.none()
        return Installation.objects.filter(organization__employees__employee_profile__user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return InstallationCreateSerializer
        return self.serializer_class

    @swagger_auto_schema(
        operation_description="Create new installation",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        from open_schools_platform.organization_management.organizations.selectors import get_organization
        
        org_id = serializer.validated_data["organization"].id
        app_id = serializer.validated_data["app"].id
        
        get_organization(filters={"id": org_id}, user=self.request.user)

        existing_installation = Installation.all_objects.filter(
            app_id=app_id,
            organization_id=org_id,
        ).first()

        if existing_installation:
            if not existing_installation.deleted:
                raise AlreadyExists("This app already installed for that organization")
            
            existing_installation.deleted = None
            existing_installation.active = True
            existing_installation.granted_scopes = serializer.validated_data.get("granted_scopes", "")
            existing_installation.user = self.request.user
            existing_installation.save()
            return

        app = App.objects.get(id=app_id)
        if app.status != AppStatus.PUBLISHED:
            raise InvalidArgument("App with such id don't available now")

        serializer.save(active=True, user=self.request.user)

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

    filterset_class = InstallationFilterset
    pagination_class = DefaultListPagination
    serializer_class = InstallationListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Installation.objects.select_related("app", "organization").all()
        if user.is_authenticated and user.is_admin:
            return qs
        if not user.is_authenticated:
            return qs.none()
        return qs.filter(organization__employees__employee_profile__user=user)

    @swagger_auto_schema(
        operation_description="Get a list of installations filtered by school, app, and status",
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        responses={200: InstallationListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)