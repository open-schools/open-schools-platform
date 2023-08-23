from open_schools_platform.common.constants import EmailConstants, CommonConstants, NewUserMessageType
from open_schools_platform.common.services import exception_if_email_service_unavailable
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.parent_management.parents.models import ParentProfile
from django.utils.translation import gettext_lazy as _

from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.services import generate_user_password, create_user
from open_schools_platform.tasks.tasks import send_message_to_new_user_with_celery


def get_parent_profile_or_create_new_user(phone: str, email: str, circle: Circle, student_name) -> ParentProfile:
    user = get_user(filters={"phone": phone})

    if not user:
        user = send_email_to_new_parent(circle.name, email, phone, user, student_name)

    return user.parent_profile


def send_email_to_new_parent(circle_name, email, phone, user, student_name):
    exception_if_email_service_unavailable()
    pwd = generate_user_password()
    subject = _('Circle invitation')
    name = _('Parent')
    send_message_to_new_user_with_celery.delay(subject,
                                               {'login': phone, 'password': pwd, 'circle': circle_name,
                                                'name': name, 'domain': CommonConstants.OPEN_SCHOOLS_DOMAIN},
                                               EmailConstants.DEFAULT_FROM_EMAIL, email,
                                               {'phone': phone, 'user_password': pwd, 'name': student_name},
                                               NewUserMessageType.InviteParent)
    user = create_user(phone=phone, password=pwd, name=name, email=email)
    return user


def get_parent_family_or_create_new(parent_profile: ParentProfile):
    family = get_family(filters={"parent_profiles": str(parent_profile.id)})

    if not family:
        family = create_family(parent=parent_profile)

    return family
