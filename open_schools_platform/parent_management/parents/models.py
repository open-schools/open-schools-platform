import uuid

from django.db import models

from open_schools_platform.common.models import BaseModel
from open_schools_platform.user_management.users.models import User


class ParentProfileManager(models.Manager):
    def create_parent_profile(self, user: User, name: str):
        parent_profile = self.model(
            name=name,
            user=user
        )
        parent_profile.full_clean()
        parent_profile.save(using=self.db)
        return parent_profile


class ParentProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    name = models.CharField(max_length=200)
    objects = ParentProfileManager()

    def __str__(self):
        return self.name.__str__()
