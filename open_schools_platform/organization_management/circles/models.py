import uuid

from django.db import models

from open_schools_platform.common.models import BaseModel
from open_schools_platform.organization_management.organizations.models import Organization


class Circle(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, related_name="circles", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
