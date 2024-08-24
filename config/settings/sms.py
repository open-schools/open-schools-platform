from config.env import env
from open_schools_platform.utils.sms_utils import SmsCenter

SMS_SERVICE_TRANSPORT = env("SMS_SERVICE_TRANSPORT", default=None)

SMS_TRANSPORT = None

if SMS_SERVICE_TRANSPORT == "SMSC":
    SMS_TRANSPORT = SmsCenter(env("SMSC_USERNAME"), env("SMSC_PASSWORD"), env("SMSC_SENDER_NAME_ID", default=None))
