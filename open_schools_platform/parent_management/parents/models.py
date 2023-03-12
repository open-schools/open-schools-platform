import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.errors.exceptions import AlreadyExists
from open_schools_platform.user_management.users.models import User


class ParentProfileManager(BaseManager):
    def create_parent_profile(self, user: User, name: str):
        try:
            parent_profile = self.get(user=user)
        except ParentProfile.DoesNotExist:
            parent_profile = None
        if parent_profile and not parent_profile.deleted:
            raise AlreadyExists("ParentProfile with this user already exists")

        parent_profile = self.update_or_create_with_check(user=user, defaults={'name': name})
        return parent_profile


class ParentProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    name = models.CharField(max_length=200)
    history = HistoricalRecords()

    objects = ParentProfileManager()  # type: ignore[assignment]

    def __str__(self):
        return self.name.__str__()
