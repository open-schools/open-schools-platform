from django.utils import timezone
from django_otp.oath import TOTP
import time
import datetime


class OTPFromPhoneNumber:
    LIVE_TIME = datetime.timedelta(minutes=7)
    otp = None
    otp_creation_date = None

    def __init__(self, phone_number):
        # secret key that will be used to generate a token
        self.key = str(phone_number).encode()
        self.verified = False
        self.number_of_digits = 6
        self.token_validity_period = int(self.LIVE_TIME.total_seconds())
        self.generate_otp()

    def totp_obj(self):
        totp = TOTP(
            key=self.key, step=self.token_validity_period, digits=self.number_of_digits
        )
        totp.time = time.time()
        return totp

    def generate_otp(self):
        self.otp = self.totp_obj()
        self.otp_creation_date = timezone.now()

    def get_otp(self):
        return str(self.otp.token()).zfill(6)

    def get_otp_creation_date(self):
        return self.otp_creation_date