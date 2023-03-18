import warnings
from enum import Enum

from config.env import env
from open_schools_platform.user_management.users.tests.constants.test_valid_api_key import is_google_api_key_valid


class CommonConstants:
    GOOGLE_API_KEY = env("GOOGLE_API_KEY")
    GOOGLE_MAPS_API_KEY = env("GOOGLE_MAPS_API_KEY", default=None)
    FIREBASE_URL_TO_GET_SESSION = r"https://www.googleapis.com/identitytoolkit" \
                                  r"/v3/relyingparty/sendVerificationCode?key="
    FIREBASE_URL_TO_CHECK_OTP = r"https://www.googleapis.com/identitytoolkit/v3" \
                                r"/relyingparty/verifyPhoneNumber?key="
    FCM_URL_TO_VALIDATE_NOTIFICATIONS_TOKEN = "https://fcm.googleapis.com/fcm/send"
    SMS_PROVIDER_URL = r"https://sms.ru/sms/send"
    SMS_API_KEY = env("SMS_API_KEY", default=None)
    FCM_SERVER_KEY = env("FCM_SERVER_KEY", default=None)
    SCHOOLS_AI_URL = env("SCHOOLS_AI_URL", default=None)
    GEOPY_GEOCODE_TIMEOUT = 10

    if not is_google_api_key_valid(FIREBASE_URL_TO_GET_SESSION, GOOGLE_API_KEY):
        warnings.warn("google api key is not valid")


class EmailConstants:
    EMAIL_SERVICE_TRANSPORT = env("EMAIL_SERVICE_TRANSPORT", default=None)
    MAILGUN_SEND_EMAIL_URL = r"https://api.mailgun.net/v3/{}/messages"

    VK_EMAIL_ID = ""
    VK_EMAIL_PRIVATE_API_KEY = ""

    if EMAIL_SERVICE_TRANSPORT == "VK":
        VK_EMAIL_ID = env("VK_EMAIL_ID")
        VK_EMAIL_PRIVATE_API_KEY = env("VK_EMAIL_PRIVATE_API_KEY")

    MAILGUN_EMAIL_PRIVATE_API_KEY = ""
    if EMAIL_SERVICE_TRANSPORT == "MAILGUN":
        MAILGUN_EMAIL_PRIVATE_API_KEY = env("MAILGUN_EMAIL_PRIVATE_API_KEY")

    EMAIL_DOMAIN = env("EMAIL_DOMAIN", default='openschools.education')
    DEFAULT_FROM_EMAIL = 'inbox@openschools.education'
    TEST_EMAIL = 'test.openschools.education@mail.ru'


class NotificationType(str, Enum):
    InviteParent = 'invite-parent-query'
    TeacherReminder = 'circle-lesson'
