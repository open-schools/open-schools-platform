import json
import os
from typing import Optional

import requests
from django.db import transaction
from phonenumber_field.modelfields import PhoneNumberField

from open_schools_platform.common.services import model_update

from open_schools_platform.users.models import User, CreationToken
from open_schools_platform.users.selectors import get_token_by_phone
from open_schools_platform.users.serializers import CreationTokenSerializer
from datetime import timezone, datetime
import datetime as datetime_lib


class RegistrationConstants:
    LIVE_TIME = datetime_lib.timedelta(minutes=7)
    FIREBASE_URL_TO_GET_SESSION = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key="
    FIREBASE_URL_TO_CHECK_OTP = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber?key="
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


def is_token_alive(token: CreationToken):
    return (datetime.now(timezone.utc) - token.created_at) < RegistrationConstants.LIVE_TIME


def create_token(data) -> CreationToken or None:
    response = send_sms(data["phone"], data["recaptcha"])

    if response.status_code == 200:
        token = CreationToken.objects.create_token(
            phone=data["phone"],
            session=json.loads(response.content.decode("utf-8"))["sessionInfo"],
        )
        return token
    return None

def update_token(token: CreationToken, token_ser) -> CreationToken:
    tuple = model_update(
        instance=token,
        fields=['recaptcha', 'session'],
        data={"recaptcha": token_ser.recaptcha,
              "session": send_sms(token_ser.recaptcha,
                                  token_ser.phone)}
    )
    if not tuple[1]:
        raise Exception("Can't edit the creation token")
    return tuple[0]


def send_sms(phone, recaptcha):
    base_url = RegistrationConstants.FIREBASE_URL_TO_GET_SESSION + \
               RegistrationConstants.GOOGLE_API_KEY

    dict = {
        "phoneNumber": phone,
        "recaptchaToken": recaptcha,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=dict)
    return response
    #return json.loads(response.content.decode("utf-8"))["sessionInfo"]


def check_otp(session, otp):
    base_url = RegistrationConstants.FIREBASE_URL_TO_CHECK_OTP + RegistrationConstants.GOOGLE_API_KEY

    dict = {
        "sessionInfo": session,
        "code": otp,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=dict)
    return response

def user_create(
    *,
    phone: PhoneNumberField,
    is_active: bool = True,
    is_admin: bool = False,
    password: Optional[str] = None
) -> User:
    user = User.objects.create_user(
        phone=phone,
        is_active=is_active,
        is_admin=is_admin,
        password=password
    )

    return user

def create_user(phone: PhoneNumberField) -> User:
    user = User.objects.create_user(
        phone=phone,
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
