from config.env import env
from open_schools_platform.utils.email_utils import VKEmailService, MailgunEmailService

transport = env("EMAIL_SERVICE_TRANSPORT", default=None)

EMAIL_TRANSPORT = None

if transport == "VK":
    EMAIL_TRANSPORT = VKEmailService
elif transport == "MAILGUN":
    EMAIL_TRANSPORT = MailgunEmailService
