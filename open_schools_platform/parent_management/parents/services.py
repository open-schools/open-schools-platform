from django.db.models import QuerySet, Max, Subquery

from open_schools_platform.common.constants import EmailConstants, CommonConstants, NewUserMessageType
from open_schools_platform.common.services import email_service
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.parent_management.parents.models import ParentProfile
from django.utils.translation import gettext_lazy as _

from open_schools_platform.ticket_management.tickets.models import Ticket
from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.services import generate_user_password, create_user
from open_schools_platform.tasks.tasks import send_message_to_new_user_with_celery


def get_parent_profile_or_create_new_user(phone: str, email: str, circle: Circle, student_name) -> ParentProfile:
    user = get_user(filters={"phone": phone})

    if not user:
        user = send_email_to_new_parent(circle.name, email, phone, user, student_name)

    return user.parent_profile


def send_email_to_new_parent(circle_name, email, phone, user, student_name):
    with email_service():
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


def get_last_organization_tickets(qs: QuerySet[Ticket]) -> QuerySet[Ticket]:
    max_dates = qs.values('recipient_id').annotate(max_created_at=Max('created_at')).values('max_created_at')
    return qs.filter(
        created_at__in=Subquery(max_dates)
    )
