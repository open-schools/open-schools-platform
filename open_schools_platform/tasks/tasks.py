from django.template.loader import render_to_string

from sendbox_sdk.api import SendBoxApi
from .celery import app
from open_schools_platform.common.constants import CommonConstants


@app.task
def send_mail_to_new_user_with_celery(subject, html_kwargs, from_email, to, template='new_user_invite_mail_form.html'):
    sdk = SendBoxApi(CommonConstants.EMAIL_ID, CommonConstants.EMAIL_PRIVATE_API_KEY)
    html = render_to_string(template, html_kwargs)
    sdk.send_html_email(subject, from_email, 'Открытые Школы', to, 'Уважаемый пользователь', html, '')
