import requests

from open_schools_platform.user_management.users.constants import RegistrationConstants


def send_sms(phone: str, recaptcha: str):
    base_url = RegistrationConstants.FIREBASE_URL_TO_GET_SESSION + \
               str(RegistrationConstants.GOOGLE_API_KEY)

    request_dict = {
        "phoneNumber": phone,
        "recaptchaToken": recaptcha,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=request_dict)
    return response


def check_otp(session: str, otp: str):
    base_url = RegistrationConstants.FIREBASE_URL_TO_CHECK_OTP + str(RegistrationConstants.GOOGLE_API_KEY)

    request_dict = {
        "sessionInfo": session,
        "code": otp,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=request_dict)
    return response
