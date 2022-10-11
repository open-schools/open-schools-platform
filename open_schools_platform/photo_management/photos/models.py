import uuid
from django.db import models
from config.settings.object_storage import ClientDocsStorage
from open_schools_platform.common.models import BaseModel


class Photo(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    image = models.ImageField(storage=ClientDocsStorage(), default=None, blank=True, null=True)
