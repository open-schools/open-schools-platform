import os
import warnings

from open_schools_platform.user_management.users.tests.constants.test_valid_api_key import is_google_api_key_valid


class CommonConstants:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
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

    # Email settings
    EMAIL_ID = os.environ.get("EMAIL_ID")
    if not EMAIL_ID:
        warnings.warn("email_id is not defined")
    EMAIL_DOMAIN = 'openschools.education'
    DEFAULT_FROM_EMAIL = 'inbox@openschools.education'
    EMAIL_PRIVATE_API_KEY = os.environ.get("EMAIL_PRIVATE_API_KEY")
    USING_BACKUP_EMAIL = os.environ.get("BACKUP_EMAIL_SERVICE")
    BACKUP_EMAIL_DOMAIN = os.environ.get('BACKUP_EMAIL_DOMAIN')
    BACKUP_EMAIL_PRIVATE_API_KEY = os.environ.get('BACKUP_EMAIL_PRIVATE_API_KEY')
    if not EMAIL_PRIVATE_API_KEY:
        warnings.warn("email_private_api_key is not defined")
    TEST_EMAIL = 'test.openschools.education@mail.ru'
