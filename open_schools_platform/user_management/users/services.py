from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import unix_epoch

from open_schools_platform.common.services import model_update
from open_schools_platform.user_management.users.constants import RegistrationConstants

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
    return user


@transaction.atomic
def user_update(*, user: User, data) -> User:
    non_side_effect_fields = ['first_name', 'last_name']

    user, has_updated = model_update(
        instance=user,
        fields=non_side_effect_fields,
        data=data
    )

    # Side-effect fields update here (e.g. username is generated based on first & last name)

    # ... some additional tasks with the user ...

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
