from django.template.loader import render_to_string

from sendbox_sdk.api import SendBoxApi
from open_schools_platform.common.constants import CommonConstants
from .celery import app
from ..common.services import BackupEmailService


@app.task
def send_mail_to_new_user_with_celery(subject, html_kwargs, from_email, to, template):
    html = render_to_string(template, html_kwargs)
    transport = SendBoxApi(CommonConstants.EMAIL_ID, CommonConstants.EMAIL_PRIVATE_API_KEY)
    if CommonConstants.USING_BACKUP_EMAIL:
        transport = BackupEmailService(CommonConstants.BACKUP_EMAIL_DOMAIN,
                                       CommonConstants.BACKUP_EMAIL_PRIVATE_API_KEY)
    transport.send_html_email(subject, from_email, 'Открытые Школы', to, 'Уважаемый пользователь', html, '')
