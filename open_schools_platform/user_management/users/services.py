import random

import requests
from django.contrib.auth import authenticate
from django.db import transaction
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from rest_framework import serializers
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import unix_epoch

from config.settings.push_notifications import app
from config.settings.sms import SMS_TRANSPORT
from open_schools_platform.common.constants import CommonConstants, SmsConstants
from open_schools_platform.common.services import model_update, SendSmsService
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.constants import RegistrationConstants, GenerateConstants

from open_schools_platform.user_management.users.models import User, CreationToken, FirebaseNotificationToken
from datetime import timezone, datetime


def is_token_alive(token: CreationToken) -> bool:
    return (datetime.now(timezone.utc) - token.created_at) < RegistrationConstants.LIVE_TIME


def generate_otp() -> int:
    return random.randint(10 ** (GenerateConstants.OTP_LENGTH - 1), 10 ** GenerateConstants.OTP_LENGTH - 1)


def send_otp_sms(otp: int, phone_number: str):
    return SendSmsService().sms_transport.send_sms([str(phone_number)], f"Код подтверждения: {str(otp)}",
                                  sender=SmsConstants.DEFAULT_SENDER_SMS)


def check_token_otp_match(token: CreationToken, otp: int) -> bool:
    return token.otp == otp


def create_token(phone: str, otp: int, session: str = "") -> CreationToken:
    token = CreationToken.objects.create_token(
        phone=phone,
        otp=str(otp),
        session=session,
    )
    return token


def create_user(phone: str, password: str, name: str, is_active: bool = True,
                is_admin: bool = False, email: str = '') -> User:
    user = User.objects.create_user(
        phone=phone,
        password=password,
        name=name,
        is_active=is_active,
        is_admin=is_admin,
    )
    EmployeeProfile.objects.create_employee_profile(
        user=user,
        name=name,
        email=email
    )
    ParentProfile.objects.create_parent_profile(
        name=name,
        user=user
    )
    StudentProfile.objects.create_student_profile(name=name, user=user)
    TeacherProfile.objects.create_teacher_profile(name=name, user=user)
    FirebaseNotificationToken.objects.create_token(user=user)
    return user


@transaction.atomic
def user_update(*, user: User, data) -> User:
    non_side_effect_fields = ['name']

    user, has_updated = model_update(
        instance=user,
        fields=non_side_effect_fields,
        data=data
    )
    user.employee_profile.name = user.name
    user.employee_profile.save()

    user.student_profile.name = user.name
    user.student_profile.save()

    user.parent_profile.name = user.name
    user.parent_profile.save()

    user.teacher_profile.name = user.name
    user.teacher_profile.save()
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

    response_data = JSONWebTokenAuthentication.jwt_create_response_payload(token, user, request, issued_at)

    return str(response_data["token"])


def update_token_session(token: CreationToken, new_session: str) -> CreationToken:
    token.session = new_session
    token.save()
    return token


def update_token_otp(token: CreationToken, new_otp: int) -> CreationToken:
    token.otp = str(new_otp)
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


def update_fcm_notification_token_entity(*, token: FirebaseNotificationToken, data: dict) -> FirebaseNotificationToken:
    non_side_effect_fields = ['token']
    filtered_data = filter_dict_from_none_values(data)
    token, has_updated = model_update(
        instance=token,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return token


def notify_user(user: User, title: str, body: str, data: dict = None) -> int:
    """
    notify_user returns numeric values:
        0 - User has no firebase registration token
        1 - Error occurred while sending push notification
        2 - notification was sent successfully
    """

    if user.firebase_token.token is None:
        return 0
    message = messaging.Message(
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(title=title, body=body)),
        data=data,
        token=user.firebase_token.token,
    )
    try:
        messaging.send(message, app=app)
    except FirebaseError or ValueError:
        return 1
    return 2


def is_firebase_token_valid(token: str):
    url = CommonConstants.FCM_URL_TO_VALIDATE_NOTIFICATIONS_TOKEN
    headers = {
        'Authorization': f'key={CommonConstants.FCM_SERVER_KEY}',
        'Content-Type': "application/json"
    }
    payload = {
        "registration_ids": [token],
        "dry_run": True
    }
    response = requests.post(url=url, json=payload, headers=headers)
    if {"error": "InvalidRegistration"} in response.json()["results"]:
        return False
    return True
