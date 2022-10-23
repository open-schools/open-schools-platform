import uuid

from django.db import models
from django.contrib.auth.models import (
    UserManager as BUM,
    PermissionsMixin,
    AbstractBaseUser
)
from django.db.models import Manager
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore

from open_schools_platform.common.models import BaseModel


# Taken from here:
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
# With some modifications


class UserManager(BUM):
    def create_user(self, phone, name="", is_active=True, is_admin=False, password=None):
        if not phone:
            raise ValueError('Users must have a phone number')

        user = self.model(
            phone=phone,
            is_active=is_active,
            is_admin=is_admin,
            name=name,
        )

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

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


class CreationTokenManager(Manager):
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
    firebase_token = models.CharField(max_length=200, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone.__str__()

    def get_username(self):
        return self.__str__()

    def is_staff(self):
        return self.is_admin


class CreationToken(BaseModel):
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

    objects = CreationTokenManager()

    def __str__(self):
        return self.key.__str__()
