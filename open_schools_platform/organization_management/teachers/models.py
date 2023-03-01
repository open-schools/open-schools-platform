import uuid

import safedelete
from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseManager, BaseModel
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.photo_management.photos.models import Photo
from open_schools_platform.user_management.users.models import User


class TeacherProfileManager(BaseManager):
    def create_teacher_profile(self, name: str, age: int = None, phone: PhoneNumber = None, user: User = None,
                               photo: uuid.UUID = None):
        if not photo:
            photo = Photo.objects.create_photo()

        teacher_profile = self.model(
            name=name,
            age=age,
            user=user,
            phone=phone,
            photo=photo
        )
        teacher_profile.full_clean()
        teacher_profile.save(using=self.db)
        return teacher_profile


class TeacherProfile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', null=True, blank=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    phone = PhoneNumberField(
        verbose_name='telephone number',
        max_length=17,
        blank=True,
        null=True,
    )
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    history = HistoricalRecords()

    objects = TeacherProfileManager()  # type: ignore[assignment]

    def __str__(self):
        return self.name


class TeacherManager(BaseManager):
    def create_teacher(self, name: str, circle: Circle = None, teacher_profile: TeacherProfile = None):
        teacher = self.model(
            name=name,
            circle=circle,
            teacher_profile=teacher_profile
        )
        teacher.full_clean()
        teacher.save(using=self.db)
        return teacher


class Teacher(BaseModel):
    _safedelete_policy = safedelete.config.SOFT_DELETE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, null=True, related_name="teachers", blank=True)
    teacher_profile = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, null=True, related_name="teachers",
                                        blank=True)
    history = HistoricalRecords()

    objects = TeacherManager()  # type: ignore[assignment]

    def __str__(self):
        return self.name
