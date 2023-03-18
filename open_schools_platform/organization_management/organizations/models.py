import uuid

from typing import Any


from simple_history.models import HistoricalRecords

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
            students |= circle.students.all()
        return students

    @property
    def teachers(self):
        from open_schools_platform.organization_management.teachers.models import Teacher
        teachers = Teacher.objects.none()
        for circle in self.circles.all():
            teachers |= circle.teachers.all()
        return teachers

    def __str__(self):
        return self.name
