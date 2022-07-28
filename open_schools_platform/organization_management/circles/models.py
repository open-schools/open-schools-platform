import uuid

from django.core.validators import MinValueValidator
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
    capacity = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    address = models.CharField(max_length=255, default="")
    description = models.CharField(max_length=2000, default="")

    def __str__(self):
        return self.name
