import uuid

import safedelete
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import (
    UserManager as BUM,
    PermissionsMixin,
    AbstractBaseUser
)
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel, BaseManager


# Taken from here:
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
# With some modifications


class UserManager(BaseManager, BUM):
    def create_user(self, phone, name="", is_active=True, is_admin=False, password=None):
        if not phone:
            raise ValueError('Users must have a phone number')

        try:
            user = self.get(phone=phone)
        except User.DoesNotExist:
            user = None
        if user and not user.deleted:
            raise ValidationError("User with this phone number already exists")

        user = self.update_or_create_with_check(phone=phone,
                                                defaults={'is_active': is_active, 'is_admin': is_admin,
                                                          'name': name}, password=password)

        return user

    def create_superuser(self, name, phone, is_active=True, is_admin=True, password=None):
        from open_schools_platform.user_management.users.services import create_user
        user = create_user(
            phone=phone,
            name=name,
            password=password,
            is_active=is_active,
            is_admin=is_admin,
        )

        user.is_superuser = True
        user.save(using=self._db)

        return user


class CreationTokenManager(BaseManager):
    def create_token(self, phone, session):
        if not phone:
            raise ValueError('Users must have a phone')

        token = self.model(
            phone=phone,
            session=session,
        )

        token.full_clean()
        token.save(using=self._db)

        return token


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    _safedelete_policy = safedelete.config.SOFT_DELETE_CASCADE
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    phone = PhoneNumberField(
        verbose_name='telephone number',
        max_length=17,
        unique=True,
        blank=False,
        null=True,
    )
    name = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # This should potentially be an encrypted field
    jwt_key = models.UUIDField(default=uuid.uuid4)

    last_login_ip_address = models.GenericIPAddressField(null=True, blank=True)

    history = HistoricalRecords()

    objects = UserManager()  # type: ignore[assignment] #TODO

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone.__str__()

    def get_username(self):
        return self.__str__()

    def is_staff(self):
        return self.is_admin


class FirebaseNotificationTokenCreationManager(BaseManager):
    def create_token(self, user: User, token: str = None):
        try:
            firebase_token = self.get(user=user)
        except FirebaseNotificationToken.DoesNotExist:
            firebase_token = None
        if firebase_token and not firebase_token.deleted:
            raise ValidationError("FirebaseToken with this user already exists")

        firebase_token = self.update_or_create_with_check(user=user, defaults={'token': token})
        return firebase_token


class FirebaseNotificationToken(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='firebase_token')
    token = models.CharField(max_length=200, null=True, blank=True)

    objects = FirebaseNotificationTokenCreationManager()  # type: ignore[assignment]


class CreationToken(BaseModel):
    _safedelete_policy = safedelete.config.NO_DELETE
    key = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
    )

    phone = PhoneNumberField(
        verbose_name='telephone number',
        max_length=17,
        blank=False,
        null=True,
    )
    session = models.CharField(max_length=1000, null=True)
    is_verified = models.BooleanField(default=False)

    objects = CreationTokenManager()  # type: ignore[assignment]

    def __str__(self):
        return self.key.__str__()
