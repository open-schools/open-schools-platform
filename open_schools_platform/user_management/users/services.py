from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import unix_epoch

from open_schools_platform.common.services import model_update
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.parent_management.parents.selectors import get_parent_profile
from open_schools_platform.student_management.student.models import StudentProfile
from open_schools_platform.student_management.student.selectors import get_student_profile
from open_schools_platform.user_management.users.constants import RegistrationConstants, GenerateConstants

from open_schools_platform.user_management.users.models import User, CreationToken
from datetime import timezone, datetime


def is_token_alive(token: CreationToken) -> bool:
    return (datetime.now(timezone.utc) - token.created_at) < RegistrationConstants.LIVE_TIME


def create_token(phone: str, session: str) -> CreationToken:
    token = CreationToken.objects.create_token(
        phone=phone,
        session=session,
    )
    return token


def create_user(phone: str, password: str, name: str, is_active: bool = True, is_admin: bool = False) -> User:
    user = User.objects.create_user(
        phone=phone,
        password=password,
        name=name,
        is_active=is_active,
        is_admin=is_admin,
    )
    ParentProfile.objects.create_parent_profile(
        name=name,
        user=user
    )
    StudentProfile.objects.create_student_profile(
        name=name,
        user=user
    )
    return user


@transaction.atomic
def user_update(*, user: User, data) -> User:
    non_side_effect_fields = ['name']

    user, has_updated = model_update(
        instance=user,
        fields=non_side_effect_fields,
        data=data
    )
    student_profile = get_student_profile(filters={"user": user})
    student_profile.name = user.name
    student_profile.save()

    parent_profile = get_parent_profile(filters={"user": user})
    parent_profile.name = user.name
    parent_profile.save()

    return user


def verify_token(token: CreationToken) -> CreationToken:
    token.is_verified = True
    token.save()
    return token


def get_jwt_token(username_field: str, username: str, password: str, request=None) -> str:
    credentials = {
        username_field: username,
        'password': password,
    }

    user = authenticate(**credentials)

    if not user:
        msg = 'Unable to log in with provided credentials.'
        raise serializers.ValidationError(msg)

    payload = JSONWebTokenAuthentication.jwt_create_payload(user)

    token = JSONWebTokenAuthentication.jwt_encode_payload(payload)
    issued_at = payload.get('iat', unix_epoch())

    response_data = JSONWebTokenAuthentication. \
        jwt_create_response_payload(token, user, request, issued_at)

    return str(response_data["token"])


def update_token_session(token: CreationToken, new_session: str) -> CreationToken:
    token.session = new_session
    token.save()
    return token


def generate_user_password():
    password = User.objects.make_random_password(length=GenerateConstants.PASSWORD_LENGTH,
                                                 allowed_chars=GenerateConstants.ALPHABET)
    return password


def set_new_password_for_user(user: User, password: str) -> User:
    user.set_password(password)
    user.save()
    return user
