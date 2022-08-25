from typing import Any

import uuid
from django.db import models

from open_schools_platform.common.models import BaseModel
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


class EmployeeManager(models.Manager):
    def create(self, *args: Any, **kwargs: Any):
        employee = self.model(
            *args,
            **kwargs,
        )

        employee.full_clean()
        employee.save(using=self._db)

        return employee


class EmployeeProfileManager(models.Manager):
    def create(self, *args: Any, **kwargs: Any):
        employee_profile = self.model(
            *args,
            **kwargs,
        )

        employee_profile.full_clean()
        employee_profile.save(using=self._db)

        return employee_profile


class EmployeeProfile(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(User, related_name='employee_profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    objects = EmployeeProfileManager()

    def __str__(self):
        return self.user.__str__()


class Employee(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    employee_profile = models.ForeignKey(EmployeeProfile, related_name='employees',
                                         null=True, default=None, blank=True, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='employees',
                                     null=True, default=None, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255, blank=True, default="")

    objects = EmployeeManager()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('organization', 'employee_profile')
