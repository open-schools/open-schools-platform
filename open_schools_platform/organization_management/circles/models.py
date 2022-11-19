import uuid
from typing import Any

from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator
from django.contrib.gis.db import models

from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.organization_management.organizations.models import Organization


class CircleManager(BaseManager):
    def create_circle(self, *args: Any, **kwargs: Any):
        circle = self.model(
            *args,
            **kwargs,
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
    location = models.PointField(geography=True, default=Point(0.0, 0.0))

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    def __str__(self):
        return self.name
