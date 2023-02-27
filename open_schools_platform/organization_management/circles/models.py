import datetime
import uuid
from typing import Any

import safedelete
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator
from django.contrib.gis.db import models
from django_lifecycle import hook, AFTER_SAVE, LifecycleModelMixin
from simple_history.models import HistoricalRecords

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


class Circle(LifecycleModelMixin, BaseModel):
    _safedelete_policy = safedelete.config.SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, related_name="circles", on_delete=models.CASCADE)
    objects = CircleManager()  # type: ignore[assignment]
    capacity = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    address = models.CharField(max_length=255, default="")
    description = models.CharField(max_length=2000, default="")
    location = models.PointField(geography=True, default=Point(0.0, 0.0))
    start_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    history = HistoricalRecords()

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    def __str__(self):
        return self.name

    @hook(AFTER_SAVE, when='start_time', has_changed=True)
    def on_start_time_change(self):
        from open_schools_platform.organization_management.circles.services import setup_scheduled_notifications
        setup_scheduled_notifications(self, [datetime.timedelta(days=1), datetime.timedelta(hours=1)])
