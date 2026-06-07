from django.urls import path

from open_schools_platform.marketplace_management.views import (
    AppApi,
    InstallationsViewSet,
    AdminInstallationViewSet,
    ReviewApi,
    CategoryApi,
)
from open_schools_platform.marketplace_management.oauth2_views import (
    AuthorizeView,
    TokenView,
    UserInfoView,
    RevokeTokenView,
    GenerateAuthCodeView,
)
from open_schools_platform.marketplace_management.webhooks import (
    JiraApproveWebhookView,
    ValidateCredentialsWebhookView,
    JiraUpdateAppWebhookView,
    JiraDeleteAppWebhookView,
    JiraRegenerateSecretWebhookView,
    JiraRestoreAppWebhookView,
)

app_name = "marketplace"

urlpatterns = [
    path("apps", AppApi.as_view({"get": "list"}), name="miniapps-apps-list"),
    path("apps/<uuid:pk>", AppApi.as_view({"get": "retrieve"}), name="miniapps-apps-detail"),
    path("categories", CategoryApi.as_view({"get": "list"}), name="miniapps-categories-list"),
    path("categories/<uuid:pk>", CategoryApi.as_view({"get": "retrieve"}), name="miniapps-categories-detail"),
    path("apps/<uuid:app_id>/reviews", ReviewApi.as_view({"get": "list", "post": "create"}), name="miniapps-reviews"),
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
    path("oauth2/revoke", RevokeTokenView.as_view(), name="oauth2-revoke"),
    path("auth/generate_code", GenerateAuthCodeView.as_view(), name="oauth2-generate-code"),
    path("webhooks/jira/publish-app", JiraApproveWebhookView.as_view(), name="webhook-jira-publish-app"),
    path("webhooks/jira/validate-credentials", ValidateCredentialsWebhookView.as_view(), name="webhook-jira-validate-credentials"),
    path("webhooks/jira/update-app", JiraUpdateAppWebhookView.as_view(), name="webhook-jira-update-app"),
    path("webhooks/jira/delete-app", JiraDeleteAppWebhookView.as_view(), name="webhook-jira-delete-app"),
    path("webhooks/jira/regenerate-secret", JiraRegenerateSecretWebhookView.as_view(), name="webhook-jira-regenerate-secret"),
    path("webhooks/jira/restore-app", JiraRestoreAppWebhookView.as_view(), name="webhook-jira-restore-app"),
]
