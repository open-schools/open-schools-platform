import uuid

from typing import Any

from open_schools_platform.common.models import BaseModel
from django.db import models


class OrganizationManager(models.Manager):
    def create(self, *args: Any, **kwargs: Any):
        organization = self.model(
            *args,
            **kwargs,
        )

        organization.full_clean()
        organization.save(using=self._db)

        return organization


class Organization(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=255, blank=True, default="")

    objects = OrganizationManager()

    def __str__(self):
        return self.name
