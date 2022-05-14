from django.db import models

from open_schools_platform.common.models import BaseModel
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


class Employee(BaseModel):
    user = models.ForeignKey(User, related_name='employees', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='employees', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
