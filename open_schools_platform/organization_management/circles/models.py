import uuid

from django.db import models

from open_schools_platform.common.models import BaseModel
from open_schools_platform.organization_management.organizations.models import Organization


class CircleManager(models.Manager):
    def create_circle(self, name: str, organization: Organization):
        circle = self.model(
            name=name,
            organization=organization,
        )

        circle.full_clean()
        circle.save(using=self._db)

        return circle


class Circle(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, related_name="circles", on_delete=models.CASCADE)
    objects = CircleManager()

    def __str__(self):
        return self.name
