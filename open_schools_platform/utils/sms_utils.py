from abc import ABC, abstractmethod
from typing import List, Optional

from open_schools_platform.utils.sms_center_utils import SMSC


class BaseSmsService(ABC):
    """
    This is base class for email services that allows us to send emails.

    If you want to connect another email service - follow these steps:
        1. Create new class, that will inherit from base class. After that you should override
        send_sms method with the logic, that will use your service for sending sms.
        2. Define variables that will be used by this service (for example - api_key) in
        new class constructor.
        3. Put your new class in project settings for sms.
    """
    @abstractmethod
    def send_sms(self, phones: List[str], message: str) -> bool:
        pass


class SmsCenter(BaseSmsService):
    def __init__(self, username: str, password: str, sender_name_id: Optional[str]):
        self.username = username
        self.password = password
        self.sender_name_id = sender_name_id
        self.smsc_provider = SMSC(self.username, self.password)

    def send_sms(self, phones: List[str], message: str):
        response = self.smsc_provider.send_sms(",".join(phones), message, sender=self.sender_name_id)
        return response[1] > "0"
