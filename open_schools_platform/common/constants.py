import os
import warnings

from config.env import env
from open_schools_platform.user_management.users.tests.constants.test_valid_api_key import is_google_api_key_valid


class CommonConstants:
    GOOGLE_API_KEY = env("GOOGLE_API_KEY")
    GOOGLE_MAPS_API_KEY = env("GOOGLE_MAPS_API_KEY")
    FIREBASE_URL_TO_GET_SESSION = r"https://www.googleapis.com/identitytoolkit" \
                                  r"/v3/relyingparty/sendVerificationCode?key="
    FIREBASE_URL_TO_CHECK_OTP = r"https://www.googleapis.com/identitytoolkit/v3" \
                                r"/relyingparty/verifyPhoneNumber?key="
    FCM_URL_TO_VALIDATE_NOTIFICATIONS_TOKEN = "https://fcm.googleapis.com/fcm/send"
    SMS_PROVIDER_URL = r"https://sms.ru/sms/send"
    SMS_API_KEY = os.environ.get("SMS_API_KEY")
    FCM_SERVER_KEY = os.environ.get("FCM_SERVER_KEY")
    SCHOOLS_AI_URL = os.environ.get("SCHOOLS_AI_URL")
    GEOPY_GEOCODE_TIMEOUT = 10

    if not GOOGLE_API_KEY or not is_google_api_key_valid(FIREBASE_URL_TO_GET_SESSION, GOOGLE_API_KEY):
        warnings.warn("google api key is not valid or is not defined")
    if not GOOGLE_MAPS_API_KEY:
        warnings.warn("google maps api key is not defined")


class EmailConstants:
    EMAIL_SERVICE_TRANSPORT = os.environ.get("EMAIL_SERVICE_TRANSPORT")
    MAILGUN_SEND_EMAIL_URL = r"https://api.mailgun.net/v3/{}/messages"
    VK_EMAIL_ID = os.environ.get("VK_EMAIL_ID")
    VK_EMAIL_PRIVATE_API_KEY = os.environ.get("VK_EMAIL_PRIVATE_API_KEY")
    if EMAIL_SERVICE_TRANSPORT == "VK":
        if not VK_EMAIL_ID:
            warnings.warn("vk_email_id is not defined")
        if not VK_EMAIL_PRIVATE_API_KEY:
            warnings.warn("vk_email_private_api_key is not defined")
    MAILGUN_EMAIL_PRIVATE_API_KEY = os.environ.get("MAILGUN_EMAIL_PRIVATE_API_KEY")
    if EMAIL_SERVICE_TRANSPORT == "MAILGUN":
        if not not MAILGUN_EMAIL_PRIVATE_API_KEY:
            warnings.warn("mailgun_email_private_api_key is not defined")
    EMAIL_DOMAIN = 'openschools.education'
    DEFAULT_FROM_EMAIL = 'inbox@openschools.education'
    TEST_EMAIL = 'test.openschools.education@mail.ru'
