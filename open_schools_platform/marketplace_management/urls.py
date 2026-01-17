from django.urls import path

from open_schools_platform.marketplace_management.views import (
    AppApi,
    InstallationsViewSet,
    AdminInstallationViewSet, AppReviewViewSet,
)

urlpatterns = [
    path("apps", AppApi.as_view({"get": "list"}), name="miniapps-apps-list"),
    path("apps/<uuid:pk>", AppApi.as_view({"get": "retrieve"}), name="miniapps-apps-detail"),
    path("apps/<uuid:app_id>/reviews", AppReviewViewSet.as_view({"post": "create", "get": "list"}), name="miniapps-apps-add-review"),
    path(
        "installations/<uuid:pk>",
        InstallationsViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="miniapps-installations-detail",
    ),
    path(
        "installations",
        InstallationsViewSet.as_view({"post": "create"}),
        name="miniapps-installations-create",
    ),
    path(
        "admin/installations",
        AdminInstallationViewSet.as_view({"get": "list"}),
        name="admin-installations-list",
    ),
]
