from open_schools_platform.common.models import BaseModel
from django.db import models


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=255)
