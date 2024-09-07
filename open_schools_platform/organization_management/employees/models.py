from typing import Any

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.organization_management.employees.roles import EmployeeRole
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


class EmployeeManager(BaseManager):
    def create(self, *args: Any, **kwargs: Any):
        employee = self.model(
            *args,
            **kwargs,
        )

        employee.full_clean()
        employee.save(using=self._db)

        return employee


class EmployeeProfileManager(BaseManager):
    def create_employee_profile(self, user: User, name: str, email: str = None):
        try:
            employee_profile = self.get(user=user)
        except EmployeeProfile.DoesNotExist:
            employee_profile = None
        if employee_profile and not employee_profile.deleted:
            raise ValidationError("EmployeeProfile with this user already exists")

        employee_profile = self.update_or_create_with_check(user=user, defaults={'name': name, 'email': email})
        return employee_profile


class EmployeeProfile(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(User, related_name='employee_profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, blank=True, null=True)
    history = HistoricalRecords()

    objects = EmployeeProfileManager()  # type: ignore[assignment]

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
    role = models.CharField(choices=EmployeeRole.choices, default=EmployeeRole.employee,
                            max_length=50, null=True, blank=True)
    history = HistoricalRecords()

    objects = EmployeeManager()  # type: ignore[assignment]

    def __str__(self):
        return self.name
