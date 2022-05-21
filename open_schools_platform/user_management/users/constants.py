import datetime as datetime_lib
import string


class RegistrationConstants:
    LIVE_TIME = datetime_lib.timedelta(minutes=7)


class GenerateConstants:
    alphabet = string.ascii_letters + string.digits
    password_length = 10
