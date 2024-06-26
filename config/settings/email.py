from config.env import env
from open_schools_platform.utils.email_utils import VKEmailService, MailgunEmailService, LocalEmailService

transport = env("EMAIL_SERVICE_TRANSPORT", default=None)

EMAIL_TRANSPORT = None

if transport == "VK":
    EMAIL_TRANSPORT = VKEmailService
elif transport == "MAILGUN":
    EMAIL_TRANSPORT = MailgunEmailService
    env('MAILGUN_EMAIL_PRIVATE_API_KEY')
    env('EMAIL_DOMAIN')
elif transport == "LOCAL":
    EMAIL_TRANSPORT = LocalEmailService
    env('EMAIL_USE_TLS')
    env('EMAIL_HOST')
    env('EMAIL_PORT')
    env('EMAIL_HOST_USER')
    env('EMAIL_HOST_PASSWORD')

