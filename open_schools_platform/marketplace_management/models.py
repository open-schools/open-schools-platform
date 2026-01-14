import uuid
from typing import Optional, Union, Tuple, Type, Any  # noqa: F401
from safedelete.queryset import SafeDeleteQueryset  # noqa: F401

from open_schools_platform.common.models import BaseModel
from open_schools_platform.organization_management.organizations.models import (
    Organization,
)
from open_schools_platform.user_management.users.models import User
from django.db import models


class AppType(models.TextChoices):
    INTERNAL = "internal", "Internal"
    EXTERNAL = "external", "External"


class AppStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_REVIEW = "pending_review", "Pending Review"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"


class DeveloperProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="developer_profile"
    )
    email = models.EmailField(max_length=255)
    github = models.URLField(max_length=255)


class Category(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)


class App(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=AppType.choices)
    status = models.CharField(max_length=15, choices=AppStatus.choices, default="draft")
    icon_url = models.URLField(blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    developer_profile = models.ForeignKey(
        DeveloperProfile,
        on_delete=models.CASCADE,
        related_name="apps",
    )
    category = models.ManyToManyField(Category, related_name="apps")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def latest_release(self) -> "AppRelease | None":
        return self.versions.order_by("-date").first()


class AppRelease(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    version = models.CharField(max_length=50)
    date = models.DateField()
    description = models.TextField()
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="versions")
    manifest = models.JSONField(default=dict)


class Review(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    app = models.OneToOneField(App, on_delete=models.CASCADE)
    rating = models.IntegerField()
    message = models.CharField(max_length=512)


class Installation(BaseModel):
    STATUS_DISABLED = "disabled"
    STATUS_ACTIVE = "active"
    STATUS_UNINSTALLED = "uninstalled"

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_DISABLED, "Disabled"),
        (STATUS_UNINSTALLED, "Uninstalled"),
    )

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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True,
    )
    active = models.BooleanField(default=True)
    disabled_at = models.DateTimeField(null=True, blank=True)
    re_activated_at = models.DateTimeField(null=True, blank=True)
    uninstalled_at = models.DateTimeField(null=True, blank=True)
    config_data = models.JSONField(default=dict)

    class Meta:
        unique_together = ["app", "organization"]


class InstallationStatusLog(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    installation = models.ForeignKey(
        Installation,
        on_delete=models.CASCADE,
        related_name="status_logs",
    )
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    changed_at = models.DateTimeField(auto_now_add=True)
