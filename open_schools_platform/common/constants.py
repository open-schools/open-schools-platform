import warnings
from enum import Enum

from config.env import env
from config.settings.email import EMAIL_SERVICE_TRANSPORT, EMAIL_DOMAIN
from config.settings.sms import SMS_SERVICE_TRANSPORT
from open_schools_platform.user_management.users.tests.constants.test_valid_api_key import is_google_api_key_valid


class CommonConstants:
    GOOGLE_API_KEY = env("GOOGLE_API_KEY")
    GOOGLE_MAPS_API_KEY = env("GOOGLE_MAPS_API_KEY", default=None)
    FIREBASE_URL_TO_GET_SESSION = r"https://www.googleapis.com/identitytoolkit" \
                                  r"/v3/relyingparty/sendVerificationCode?key="
    FIREBASE_URL_TO_CHECK_OTP = r"https://www.googleapis.com/identitytoolkit/v3" \
                                r"/relyingparty/verifyPhoneNumber?key="
    FCM_URL_TO_VALIDATE_NOTIFICATIONS_TOKEN = "https://fcm.googleapis.com/fcm/send"
    FCM_SERVER_KEY = env("FCM_SERVER_KEY", default=None)
    OPEN_SCHOOLS_DOMAIN = env("OPEN_SCHOOLS_DOMAIN", default="v1.openschools.education")
    GEOPY_GEOCODE_TIMEOUT = 10

    if not is_google_api_key_valid(FIREBASE_URL_TO_GET_SESSION, GOOGLE_API_KEY):
        warnings.warn("google api key is not valid")

    REGISTRATION_MESSAGES_TRANSPORT = env("REGISTRATION_MESSAGES_TRANSPORT", default="email")


class EmailConstants:
    EMAIL_SERVICE_TRANSPORT = EMAIL_SERVICE_TRANSPORT
    EMAIL_DOMAIN = EMAIL_DOMAIN
    DEFAULT_FROM_EMAIL = 'inbox@openschools.education'
    TEST_EMAIL = 'test.openschools.education@mail.ru'


class SmsConstants:
    SMS_SERVICE_TRANSPORT = SMS_SERVICE_TRANSPORT
    DEFAULT_SENDER_SMS_NAME = 'Открытые школы'


class NotificationType(str, Enum):
    InviteParent = 'invite-parent-query'
    TeacherReminder = 'circle-lesson'


class NewUserMessageType(str, Enum):
    InviteEmployee = 'invite-employee'
    InviteParent = 'invite-parent'


EmailTemplateName = {
    NewUserMessageType.InviteParent: 'new_user_circle_invite_mail_form.html',
    NewUserMessageType.InviteEmployee: 'new_user_invite_mail_form.html'
}
