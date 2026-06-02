import uuid
from typing import Optional, Union, Tuple, Type, Any  # noqa: F401
from safedelete.queryset import SafeDeleteQueryset  # noqa: F401
from django.db import models

from open_schools_platform.common.models import BaseModel
from open_schools_platform.organization_management.organizations.models import (
    Organization,
)
from open_schools_platform.user_management.users.models import User


class AppStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_REVIEW = "pending_review", "Pending Review"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"


class Category(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)


class App(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=AppStatus.choices, default=AppStatus.DRAFT)
    icon_url = models.URLField(blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    category = models.ManyToManyField(Category, related_name="apps")
    manifest = models.JSONField(default=dict, blank=True)
    client_secret = models.CharField(max_length=255, blank=True, default="")
    redirect_uris = models.JSONField(default=list, blank=True)
    grant_types = models.JSONField(default=list, blank=True)
    response_types = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    client_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)


class Review(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # ИСПРАВЛЕНО: Изменено с OneToOneField на ForeignKey (связь 1-to-N на схеме)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    message = models.CharField(max_length=512)


class Installation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="installations")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="installations",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="installations"
    )
    installed_at = models.DateTimeField(auto_now_add=True)
    config_data = models.JSONField(default=dict)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["app", "organization"]


class OAuth2AuthorizationCode(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="auth_codes"
    )
    # ДОБАВЛЕНО: Связь с таблицей Apps (client_id на схеме)
    client = models.ForeignKey(
        App, on_delete=models.CASCADE, related_name="auth_codes"
    )
    redirect_uri = models.URLField()
    auth_time = models.DateTimeField(auto_now_add=True)
    response_type = models.CharField(max_length=255)
    # ДОБАВЛЕНО: Поля из схемы, которых не было в коде
    scope = models.CharField(max_length=255, blank=True, default="")

    @property
    def name(self) -> str:
        return f"Code {self.code[:8]}... ({self.user.username if self.user else 'No User'})"


class OAuth2Token(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="oauth_tokens"
    )
    # ДОБАВЛЕНО: Связь с таблицей Apps (client_id на схеме)
    client = models.ForeignKey(
        App, on_delete=models.CASCADE, related_name="oauth_tokens"
    )
    token_type = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True)
    expires_in = models.IntegerField()
    revoked = models.BooleanField(default=False)
    # ДОБАВЛЕНО: Поле из схемы
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def name(self) -> str:
        return f"Token {self.access_token[:8]}... ({self.user.username if self.user else 'No User'})"