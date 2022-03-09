from datetime import datetime, timezone
from auth_manager.utils.otp import OTPFromPhoneNumber
from models.models import UserProfile, VerificationSession
import json
import requests as re


def create_unverified_user_profile(phone_number):
    return UserProfile.objects.create(phone_number=phone_number)


def get_userprofile_by_phone_number(phone_number):
    return UserProfile.objects.filter(
        phone_number=phone_number
    )


def create_verification_session(user_profile, session):
    otp = OTPFromPhoneNumber(user_profile.phone_number)

    return VerificationSession.objects.create(
        user_profile=user_profile,
        session=session,
        creation_date=otp.get_otp_creation_date(),
    )


def edit_verification_session(user_profile, session):
    otp = get_verification_session(user_profile)

    otp_object = OTPFromPhoneNumber(user_profile.phone_number)

    otp.session = session
    otp.creation_date = otp_object.otp_creation_date
    otp.save()

    return otp


def get_verification_session(user_profile):
    return VerificationSession.objects.filter(
        user_profile=user_profile
    ).get()


def verify_by_session_and_otp(session, otp):
    base_url = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber?key=" + googleAPIKey

    dict = {
        "sessionInfo": session,
        "code": otp,
    }

    response = re.post(base_url, headers={'Content-Type': 'application/json'}, json=dict)
    return response


googleAPIKey = "AIzaSyDMUyN4rWYXnhihnIOBYBQvA--81EsGPQ8"


def prepare_phone_number(phone_number):
    for char in r" -()":
        phone_number = phone_number.replace(char, "")
    if phone_number[0] == "8":
        phone_number = "+7" + phone_number[1:]
    if phone_number[0] == "7":
        phone_number = "+" + phone_number
    return phone_number


def send_sms(phone_number, recaptcha):
    number = prepare_phone_number(phone_number)
    base_url = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key=" + googleAPIKey

    dict = {
        "phoneNumber": number,
        "recaptchaToken": recaptcha,
    }

    response = re.post(base_url, headers={'Content-Type': 'application/json'}, json=dict)
    return json.loads(response.content.decode("utf-8"))["sessionInfo"]


def is_session_alive(creation_date):
    return (datetime.now(timezone.utc) - creation_date) < LIVE_TIME

def verify_user(user_profile):
    user_profile.is_verified = True
    user_profile.save()
    return user_profile
