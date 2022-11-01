from open_schools_platform.common.constants import CommonConstants
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.parent_management.parents.models import ParentProfile

from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.services import generate_user_password, create_user
from open_schools_platform.tasks.tasks import send_mail_to_new_user_with_celery


def get_parent_profile_or_create_new_user(phone: str, email: str, circle_name: str) -> ParentProfile:
    user = get_user(filters={"phone": phone})

    if not user:
        pwd = generate_user_password()
        subject = 'Приглашение в кружок'
        name = 'Родитель'
        send_mail_to_new_user_with_celery.delay(subject,
                                                {'login': phone, 'password': pwd, 'circle': circle_name,
                                                 'name': name},
                                                CommonConstants.DEFAULT_FROM_EMAIL,
                                                email, 'new_user_circle_invite_mail_form.html')
        user = create_user(phone=phone, password=pwd, name=name, email=email)

    return user.parent_profile


def get_parent_family_or_create_new(parent_profile: ParentProfile):
    family = get_family(filters={"parent_profiles": str(parent_profile.id)})

    if not family:
        family = create_family(parent=parent_profile)

    return family
