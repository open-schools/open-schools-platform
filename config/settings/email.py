from config.env import env
from open_schools_platform.utils.email_utils import VKEmailService, MailgunEmailService

EMAIL_SERVICE_TRANSPORT = env("EMAIL_SERVICE_TRANSPORT", default=None)
EMAIL_DOMAIN = env("EMAIL_DOMAIN", default='openschools.education')

EMAIL_TRANSPORT = None

if EMAIL_SERVICE_TRANSPORT == "VK":
    EMAIL_TRANSPORT = VKEmailService(EMAIL_DOMAIN, env("VK_EMAIL_ID"), env("VK_EMAIL_PRIVATE_API_KEY"))
elif EMAIL_SERVICE_TRANSPORT == "MAILGUN":
    EMAIL_TRANSPORT = MailgunEmailService(EMAIL_DOMAIN, env("MAILGUN_EMAIL_PRIVATE_API_KEY"))
