from abc import ABC, abstractmethod

import requests
from sendbox_sdk.api import SendBoxApi


class BaseEmailService(ABC):
    """
    This is base class for email services that allows us to send emails.

    If you want to connect another email service - follow these steps:
        1. Create new class, that will inherit from base class. After that you should override
        send_html_email method with the logic, that will use your service for sending emails.
        2. Define variables that will be used by this service (for example - api_key) in
        new class constructor.
        3. Put your new class in project settings for emails.
    """
    @abstractmethod
    def send_html_email(self, subject: str,
                        from_email: str, from_name: str,
                        to_email: str, to_name: str,
                        html: str, text: str = None) -> requests.Response:
        pass


class MailgunEmailService(BaseEmailService):
    MAILGUN_SEND_EMAIL_URL = r"https://api.mailgun.net/v3/{}/messages"

    def __init__(self, domain, mailgun_api_key):
        self.domain = domain
        self.mailgun_api_key = mailgun_api_key

    def send_html_email(self, subject: str,
                        from_email: str, from_name: str,
                        to_email: str, to_name: str,
                        html: str, text: str = None):
        url = self.MAILGUN_SEND_EMAIL_URL.format(self.domain)
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
    def __init__(self, domain, vk_email_id, vk_api_key):
        self.domain = domain
        self.vk_email_id = vk_email_id
        self.vk_api_key = vk_api_key

    def send_html_email(self, subject: str,
                        from_email: str, from_name: str,
                        to_email: str, to_name: str,
                        html: str, text: str = None):
        sdk = SendBoxApi(self.vk_email_id, self.vk_api_key)
        response = sdk.send_html_email(subject, from_email, from_name, to_email, to_name, html, text)
        return response
