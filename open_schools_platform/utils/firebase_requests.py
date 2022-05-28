import requests

from open_schools_platform.common.constants import CommonConstants


def send_firebase_sms(phone: str, recaptcha: str):
    base_url = CommonConstants.FIREBASE_URL_TO_GET_SESSION + \
               str(CommonConstants.GOOGLE_API_KEY)

    request_dict = {
        "phoneNumber": phone,
        "recaptchaToken": recaptcha,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=request_dict)
    return response


def check_otp(session: str, otp: str):
    base_url = CommonConstants.FIREBASE_URL_TO_CHECK_OTP + str(CommonConstants.GOOGLE_API_KEY)

    request_dict = {
        "sessionInfo": session,
        "code": otp,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=request_dict)
    return response
