from django.urls import path

from open_schools_platform.marketplace_management.views import (
    AppApi,
    InstallationsViewSet,
    AdminInstallationViewSet,
)

urlpatterns = [
    path("apps", AppApi.as_view({"get": "list"}), name="miniapps-apps-list"),
    path(
        "installations/<uuid:pk>",
        InstallationsViewSet.as_view(
            {"get": "retrieve", "delete": "destroy"}
        ),
        name="miniapps-installations-detail",
    ),
    path(
        "installations/<uuid:pk>/status",
        InstallationsViewSet.as_view({"patch": "change_status"}),
        name="installations-change-status",
    ),
    path(
        "installations",
        InstallationsViewSet.as_view(
            {"post": "create"}
        ),
        name="miniapps-installations-create",
    ),
    path(
        "admin/installations",
        AdminInstallationViewSet.as_view({"get": "list"}),
        name="admin-installations-list",
    ),
]
