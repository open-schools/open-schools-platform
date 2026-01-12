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
        InstallationsViewSet.as_view({"get": "retrieve", "post": "create"}),
        name="miniapps-installations-detail",
    ),
    path(
        "installations/<uuid:pk>/status",
        InstallationsViewSet.as_view({"patch": "change_status"}),
        name="installations-change-status",
    ),
    path(
        "admin/installations",
        AdminInstallationViewSet.as_view({"get": "list"}),
        name="admin-installations-list",
    ),
]
