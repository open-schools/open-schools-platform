from django.urls import path

from open_schools_platform.marketplace_management.views import (
    AppApi,
    InstallationsViewSet,
)

urlpatterns = [
    path("/apps/", AppApi.as_view({"get": "list"}), name="miniapps-apps-list"),
    path(
        "/installations/<int:pk>/",
        InstallationsViewSet.as_view({"get": "retrieve", "post": "create"}),
        name="miniapps-installations-detail",
    ),
]
