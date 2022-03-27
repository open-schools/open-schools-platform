import json

import requests
from django.db import transaction

from open_schools_platform.common.services import model_update
from open_schools_platform.users.constants import RegistrationConstants

from open_schools_platform.users.models import User, CreationToken
from datetime import timezone, datetime


def is_token_alive(token: CreationToken):
    return (datetime.now(timezone.utc) - token.created_at) < RegistrationConstants.LIVE_TIME


def create_token(phone: str, recaptcha: str) -> CreationToken or None:
    response = send_sms(phone, recaptcha)

    if response.status_code == 200:
        token = CreationToken.objects.create_token(
            phone=phone,
            session=json.loads(response.content.decode("utf-8"))["sessionInfo"],
        )
        return token
    return None


def send_sms(phone: str, recaptcha: str):
    base_url = RegistrationConstants.FIREBASE_URL_TO_GET_SESSION + \
               RegistrationConstants.GOOGLE_API_KEY

    dict = {
        "phoneNumber": phone,
        "recaptchaToken": recaptcha,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=dict)
    return response


def check_otp(session: str, otp: str):
    base_url = RegistrationConstants.FIREBASE_URL_TO_CHECK_OTP + RegistrationConstants.GOOGLE_API_KEY

    dict = {
        "sessionInfo": session,
        "code": otp,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=dict)
    return response


def create_user(phone: str, password: str, name: str) -> User:
    user = User.objects.create_user(
        phone=phone,
        password=password,
        name=name,
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


def verify_token(token: CreationToken):
    token.is_verified = True
    token.save()
    return token
