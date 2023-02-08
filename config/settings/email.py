from config.env import env
from open_schools_platform.utils.email_utils import VKEmailService

transport = env("EMAIL_SERVICE_TRANSPORT")

if transport == "VK":
    email_transport = VKEmailService


class SendEmailService:
    def __init__(self):
        self.email_transport = email_transport
