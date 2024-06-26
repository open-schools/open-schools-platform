from abc import ABC, abstractmethod

import requests
from sendbox_sdk.api import SendBoxApi

from open_schools_platform.common.constants import EmailConstants
from django.core.mail import send_mail


class BaseEmailService(ABC):
    """
    This is base class for email services that allows us to send emails.

    If you want to connect another email service - follow these steps:
        1. Define variables that will be used by this service (for example - api_key) in
        base class constructor.
        2. Create new class, that will inherit from base class. After that you should override
        send_html_email method with the logic, that will use your service for sending emails.
        3. Put your new class in project settings for emails.
    """
    def __init__(self):
        self.vk_api_key = EmailConstants.VK_EMAIL_PRIVATE_API_KEY
        self.vk_email_id = EmailConstants.VK_EMAIL_ID
        self.domain = EmailConstants.EMAIL_DOMAIN
        self.mailgun_api_key = EmailConstants.MAILGUN_EMAIL_PRIVATE_API_KEY

    @abstractmethod
    def send_html_email(self, subject: str,
                        from_email: str, from_name: str,
                        to_email: str, to_name: str,
                        html: str, text: str = None):
        pass


class MailgunEmailService(BaseEmailService):
    def send_html_email(self, subject: str,
                        from_email: str, from_name: str,
                        to_email: str, to_name: str,
                        html: str, text: str = None):
        url = EmailConstants.MAILGUN_SEND_EMAIL_URL.format(self.domain)
        response = requests.post(
            url,
            auth=("api", self.mailgun_api_key),
            data={"from": f'{from_name} <{from_email}>',
                  "to": [f'{to_email}', f'{to_name}'],
                  "subject": subject,
                  "text": text,
                  "html": html})
        return response


class VKEmailService(BaseEmailService):
    def send_html_email(self, subject: str,
                        from_email: str, from_name: str,
                        to_email: str, to_name: str,
                        html: str, text: str = None):
        sdk = SendBoxApi(self.vk_email_id, self.vk_api_key)
        response = sdk.send_html_email(subject, from_email, from_name, to_email, to_name, html, text)
        return response


class LocalEmailService(BaseEmailService):
    def send_html_email(self, subject: str,
                        from_email: str, from_name: str,
                        to_email: str, to_name: str,
                        html: str, text: str = None):
        send_mail(
            subject,
            html,
            from_email,
            [to_email],
            fail_silently=False
        )

