import os
import datetime as datetime_lib
import warnings

from open_schools_platform.users.tests.constants.test_valid_api_key import is_google_api_key_valid


class RegistrationConstants:
    LIVE_TIME = datetime_lib.timedelta(minutes=7)
    FIREBASE_URL_TO_GET_SESSION = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key="
    FIREBASE_URL_TO_CHECK_OTP = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber?key="
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

    if not GOOGLE_API_KEY or not is_google_api_key_valid(FIREBASE_URL_TO_GET_SESSION, GOOGLE_API_KEY):
        warnings.warn("google api key is not valid or is not defined")