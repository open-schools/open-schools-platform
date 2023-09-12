import datetime
import uuid
from typing import Any

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator
from django.contrib.gis.db import models
from django_lifecycle import hook, AFTER_SAVE, LifecycleModelMixin
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.models import Query


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, related_name="circles", on_delete=models.CASCADE)
    capacity = models.IntegerField(validators=[MinValueValidator(0)], default=0, blank=True, null=True)
    address = models.CharField(max_length=255, default="")
    description = models.CharField(max_length=2000, default="", blank=True, null=True)
    location = models.PointField(geography=True, default=Point(0.0, 0.0))
    start_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    recipient_queries = GenericRelation(Query, "recipient_id", "recipient_ct")
    history = HistoricalRecords()

    objects = CircleManager()  # type: ignore[assignment]

    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x

    @property
    def student_profile_queries(self):
        from open_schools_platform.student_management.students.models import StudentProfile
        from open_schools_platform.student_management.students.models import Student

        return self.recipient_queries.all().filter(
            sender_ct=ContentType.objects.get_for_model(StudentProfile),
            body_ct=ContentType.objects.get_for_model(Student)
        )

    def __str__(self):
        return self.name

    # TODO: locate this logic to service layer without local import?
    @hook(AFTER_SAVE, when='start_time', has_changed=True)
    def on_start_time_change(self):
        from open_schools_platform.organization_management.circles.services import setup_scheduled_notifications
        setup_scheduled_notifications(self, [datetime.timedelta(days=1), datetime.timedelta(hours=1)])
