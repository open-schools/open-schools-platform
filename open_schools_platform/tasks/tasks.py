from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .celery import app
from ..common.constants import NotificationType, CommonConstants, EmailTemplateName, NewUserMessageType
from ..common.services import SendEmailService
from ..organization_management.circles.constants import CirclesConstants
from ..sms.services import send_sms_to_parent, send_sms_to_employee
from ..user_management.users.services import notify_user


@app.task
def send_message_to_new_user_with_celery(subject, html_kwargs, from_email, to_email, sms_kwargs, message_type):
    if CommonConstants.REGISTRATION_MESSAGES_TRANSPORT == 'sms':
        if message_type == NewUserMessageType.InviteParent:
            send_sms_to_parent(**sms_kwargs)
        elif message_type == NewUserMessageType.InviteEmployee:
            send_sms_to_employee(**sms_kwargs)
    elif CommonConstants.REGISTRATION_MESSAGES_TRANSPORT == 'email':
        template = EmailTemplateName.get(message_type)
        if template:
            html = render_to_string(template, html_kwargs)
            SendEmailService().email_transport.send_html_email(subject, from_email, _('Open Schools'), to_email,
                                                               _('Dear user'), html, '')


@app.task
def send_circle_lesson_notification(circle_id):
    from open_schools_platform.organization_management.circles.selectors import get_circle
    circle = get_circle(filters={'id': circle_id})
    teachers = circle.teachers.all()
    if teachers and len(teachers) > 0:
        for teacher in teachers:
            notify_user(user=teacher.teacher_profile.user, title=CirclesConstants.NOTIFY_TEACHER_TITLE,
                        body=CirclesConstants.get_invite_teacher_message(circle.name, circle.start_time),
                        data={"circle": str(circle.id), "type": NotificationType.TeacherReminder})
