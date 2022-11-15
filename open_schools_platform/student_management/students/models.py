import uuid

import safedelete.models
from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[name-defined]
from phonenumber_field.phonenumber import PhoneNumber
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.photo_management.photos.models import Photo  # type: ignore
from open_schools_platform.user_management.users.models import User  # type: ignore[misc,name-defined]
from open_schools_platform.organization_management.circles.models import Circle


class StudentProfileManager(BaseManager):
    def create_student_profile(self, name: str, age: int = None, phone: PhoneNumber = None,
                               user: User = None, photo: uuid.UUID = None):
        student_profile = self.model(
            name=name,
            age=age,
            user=user,
            phone=phone,
            photo=photo
        )
        student_profile.full_clean()
        student_profile.save(using=self.db)
        return student_profile


class StudentProfile(BaseModel):
    _safedelete_policy = safedelete.config.SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    phone = PhoneNumberField(
        verbose_name='telephone number',
        max_length=17,
        blank=True,
        null=True,
    )
    photo = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, related_name="photo", blank=True)

    objects = StudentProfileManager()

    def __str__(self):
        return self.name.__str__()


class StudentManager(BaseManager):
    def create_student(self, name: str, circle: Circle = None, student_profile: StudentProfile = None):
        student = self.model(
            name=name,
            circle=circle,
            student_profile=student_profile
        )
        student.full_clean()
        student.save(using=self.db)
        return student


class Student(BaseModel):
    _safedelete_policy = safedelete.config.SOFT_DELETE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, null=True, related_name="students", blank=True)
    student_profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, related_name="students",
                                        blank=True)
    history = HistoricalRecords()

    objects = StudentManager()

    def __str__(self):
        return self.name


class StudentProfileCircleAdditional(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    student_phone = PhoneNumberField(
        verbose_name='telephone number',
        max_length=17,
        blank=True,
        default="",
        null=True,
    )
    parent_phone = PhoneNumberField(
        verbose_name='telephone number',
        max_length=17,
        blank=True,
        default="",
        null=True,
    )
    parent_name = models.CharField(max_length=255, blank=True, default="", null=True)
    text = models.CharField(max_length=255, blank=True, default="", null=True)
