import os

from open_schools_platform.utils.email_utils import VKEmailService, MailgunEmailService

transport = os.environ.get("EMAIL_SERVICE_TRANSPORT")

EMAIL_TRANSPORT = None

if transport == "VK":
    EMAIL_TRANSPORT = VKEmailService
elif transport == "MAILGUN":
    EMAIL_TRANSPORT = MailgunEmailService
