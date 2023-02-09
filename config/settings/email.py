import os

from open_schools_platform.utils.email_utils import VKEmailService, MailgunEmailService

transport = os.environ.get("EMAIL_SERVICE_TRANSPORT")

if not transport:
    EMAIL_TRANSPORT = None
elif transport == "VK":
    EMAIL_TRANSPORT = VKEmailService
elif transport == "MAILGUN":
    EMAIL_TRANSPORT = MailgunEmailService
