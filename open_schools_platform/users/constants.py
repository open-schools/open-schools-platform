import os
import datetime as datetime_lib


class RegistrationConstants:
    LIVE_TIME = datetime_lib.timedelta(minutes=7)
    FIREBASE_URL_TO_GET_SESSION = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key="
    FIREBASE_URL_TO_CHECK_OTP = r"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber?key="
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")