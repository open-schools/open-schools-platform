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
        InstallationsViewSet.as_view({"get": "retrieve", "post": "create", "delete": "destroy"}),
        name="miniapps-installations-detail",
    ),
    path(
        "admin/installations",
        AdminInstallationViewSet.as_view({"get": "list"}),
        name="admin-installations-list",
    ),
]
