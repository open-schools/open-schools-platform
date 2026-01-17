from django.urls import path

from open_schools_platform.marketplace_management.views import (
    AppApi,
    InstallationsViewSet,
    AppReviewViewSet,
)

urlpatterns = [
    path("apps", AppApi.as_view({"get": "list"}), name="miniapps-apps-list"),
    path(
        "apps/<uuid:pk>",
        AppApi.as_view({"get": "retrieve"}),
        name="miniapps-apps-detail",
    ),
    path(
        "apps/<uuid:app_id>/reviews",
        AppReviewViewSet.as_view({"post": "create", "get": "list"}),
        name="miniapps-apps-add-review",
    ),
    path(
        "installations/<uuid:pk>",
        InstallationsViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="miniapps-installations-detail",
    ),
    path(
        "installations/<uuid:pk>/status",
        InstallationsViewSet.as_view({"patch": "change_status"}),
        name="installations-change-status",
    ),
    path(
        "installations",
        InstallationsViewSet.as_view({"post": "create", "get": "list"}),
        name="miniapps-installations-create",
    ),
    # path(
    #     "admin/installations",
    #     AdminInstallationViewSet.as_view({"get": "list"}),
    #     name="admin-installations-list",
    # ),
]
