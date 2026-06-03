from django.urls import path

from open_schools_platform.marketplace_management.views import (
    AppApi,
    InstallationsViewSet,
    AdminInstallationViewSet,
)
from open_schools_platform.marketplace_management.oauth2_views import (
    AuthorizeView,
    TokenView,
    UserInfoView,
)
from open_schools_platform.marketplace_management.webhooks import JiraApproveWebhookView

app_name = "marketplace"

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
    path("oauth2/authorize", AuthorizeView.as_view(), name="oauth2-authorize"),
    path("oauth2/token", TokenView.as_view(), name="oauth2-token"),
    path("oauth2/userinfo", UserInfoView.as_view(), name="oauth2-userinfo"),
    path("webhooks/jira/publish-app/", JiraApproveWebhookView.as_view(), name="webhook-jira-publish-app"),
]
