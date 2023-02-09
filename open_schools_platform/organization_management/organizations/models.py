import uuid

from typing import Any


from simple_history.models import HistoricalRecords
import safedelete

from open_schools_platform.common.models import BaseModel, BaseManager
from django.db import models


class OrganizationManager(BaseManager):
    def create(self, *args: Any, **kwargs: Any):
        organization = self.model(
            *args,
            **kwargs,
        )

        organization.full_clean()
        organization.save(using=self._db)

        return organization


class Organization(BaseModel):
    _safedelete_policy = safedelete.config.SOFT_DELETE_CASCADE
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=255, blank=True, default="")
    history = HistoricalRecords()

    objects = OrganizationManager()  # type: ignore[assignment]

    @property
    def students(self):
        from open_schools_platform.student_management.students.models import Student
        students = Student.objects.none()
        for circle in self.circles.all():
            students |= circle.students
        return students

    def __str__(self):
        return self.name
