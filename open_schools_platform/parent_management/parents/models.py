import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.user_management.users.models import User


class ParentProfileManager(BaseManager):
    def create_parent_profile(self, user: User, name: str):
        parent_profile: ParentProfile
        parent_profile, created = self.update_or_create(user=user, defaults={'name': name})  # type:ignore[assignment]

        parent_profile.full_clean()
        parent_profile.save(using=self.db)
        return parent_profile


class ParentProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    name = models.CharField(max_length=200)
    history = HistoricalRecords()

    objects = ParentProfileManager()

    def __str__(self):
        return self.name.__str__()
