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


class App(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=AppStatus.choices, default=AppStatus.DRAFT)
    icon_url = models.URLField(blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    
    # На схеме это просто колонка category_name в таблице Apps, а не ManyToMany
    category_name = models.CharField(max_length=255, blank=True, default="")
    
    # OAuth Fields
    client_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    client_secret = models.CharField(max_length=255, blank=True, default="")
    redirect_uris = models.JSONField(default=list, blank=True)
    grant_types = models.JSONField(default=list, blank=True)
    response_types = models.JSONField(default=list, blank=True)
    
    required_scopes = models.JSONField(default=list, blank=True)
    optional_scopes = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # На схеме стоит 'N' со стороны Reviews, значит связи ForeignKey, а не OneToOne
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    message = models.TextField(max_length=512)  # Используем TextField или CharField на 512

    def __str__(self):
        return f"Review by {self.user} for {self.app}"


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
    
    # Поля из вашей старой модели (на схеме их явно нет, но они полезны для логики)
    config_data = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    granted_scopes = models.CharField(max_length=255, default="", blank=True)

    class Meta:
        unique_together = ["app", "organization"]

    def __str__(self):
        return f"{self.app.name} installed in {self.organization.name}"


class OAuth2AuthorizationCode(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="auth_codes"
    )
    # Связь с App (client_id на схеме указывает сюда)
    app = models.ForeignKey(
        App, to_field="client_id", on_delete=models.CASCADE, related_name="auth_codes"
    )
    redirect_uri = models.URLField()
    response_type = models.CharField(max_length=255)
    scope = models.CharField(max_length=255, blank=True, default="")  # Есть на схеме
    auth_time = models.DateTimeField(auto_now_add=True)

    @property
    def name(self) -> str:
        return f"Code {self.code[:8]}... ({self.user.username if self.user else 'No User'})"


class OAuth2Token(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="oauth_tokens"
    )
    # Связь с App (client_id на схеме указывает сюда)
    app = models.ForeignKey(
        App, to_field="client_id", on_delete=models.CASCADE, related_name="oauth_tokens"
    )
    access_token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True)
    token_type = models.CharField(max_length=255)
    expires_in = models.IntegerField()
    scope = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)  # Есть на схеме
    revoked = models.BooleanField(default=False)

    @property
    def name(self) -> str:
        return f"Token {self.access_token[:8]}... ({self.user.username if self.user else 'No User'})"