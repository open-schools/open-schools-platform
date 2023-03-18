import uuid
from django.db import models
from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.common.services import file_generate_upload_path


class PhotoManager(BaseManager):
    def create_photo(self, image: bytes = None):
        photo = self.model(
            image=image
        )
        photo.full_clean()
        photo.save(using=self.db)
        return photo


class Photo(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    image = models.ImageField(upload_to=file_generate_upload_path, default=None, blank=True, null=True)

    objects = PhotoManager()  # type: ignore[assignment]

    def __str__(self):
        return self.id.__str__()
