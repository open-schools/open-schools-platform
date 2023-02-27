import requests
from requests import Response

from open_schools_platform.common.constants import CommonConstants
from open_schools_platform.common.utils import get_dict_from_response


def send_firebase_sms(phone: str, recaptcha: str):
    base_url = CommonConstants.FIREBASE_URL_TO_GET_SESSION + CommonConstants.GOOGLE_API_KEY

    request_dict = {
        "phoneNumber": phone,
        "recaptchaToken": recaptcha,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=request_dict)
    return response


def check_otp_with_firebase(session: str, otp: str):
    base_url = CommonConstants.FIREBASE_URL_TO_CHECK_OTP + CommonConstants.GOOGLE_API_KEY

    request_dict = {
        "sessionInfo": session,
        "code": otp,
    }

    response = requests.post(base_url, headers={'Content-Type': 'application/json'}, json=request_dict)
    return response


def firebase_error_dict_with_additional_info(response: Response):
    try:
        additionally = get_dict_from_response(response)["error"]["message"]
    except Exception as ex:
        additionally = "Unable to determine firebase message error: " + ex.__str__()

    return {"message": "An error occurred. Probably you sent incorrect recaptcha.",
            "additionally": additionally}
