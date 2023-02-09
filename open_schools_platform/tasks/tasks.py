from django.template.loader import render_to_string

from .celery import app
from ..common.services import SendEmailService


@app.task
def send_mail_to_new_user_with_celery(subject, html_kwargs, from_email, to, template):
    html = render_to_string(template, html_kwargs)
    SendEmailService().email_transport().send_html_email(subject, from_email, 'Открытые Школы', to,
                                                         'Уважаемый пользователь', html, '')
