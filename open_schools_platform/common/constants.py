import os
import warnings

from open_schools_platform.user_management.users.tests.constants.test_valid_api_key import is_google_api_key_valid


class CommonConstants:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    FIREBASE_URL_TO_GET_SESSION = r"https://www.googleapis.com/identitytoolkit" \
                                  r"/v3/relyingparty/sendVerificationCode?key="
    FIREBASE_URL_TO_CHECK_OTP = r"https://www.googleapis.com/identitytoolkit/v3" \
                                r"/relyingparty/verifyPhoneNumber?key="
    SMS_PROVIDER_URL = r"https://sms.ru/sms/send"
    SMS_API_KEY = os.environ.get("SMS_API_KEY")
    SCHOOLS_AI_URL = os.environ.get("SCHOOLS_AI_URL")
    GEOPY_GEOCODE_TIMEOUT = 10

    if not GOOGLE_API_KEY or not is_google_api_key_valid(FIREBASE_URL_TO_GET_SESSION, GOOGLE_API_KEY):
        warnings.warn("google api key is not valid or is not defined")
