from open_schools_platform.common.constants import EmailConstants, CommonConstants, NewUserMessageType
from open_schools_platform.common.services import model_update, email_service
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.errors.exceptions import QueryCorrupted
from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.tasks.tasks import send_message_to_new_user_with_celery
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.services import create_user, generate_user_password
from django.utils.translation import gettext_lazy as _


def create_employee(name: str, position: str = "", user: User = None, organization: Organization = None) -> Employee:
    employee_profile = None
    if user:
        employee_profile = user.employee_profile

    employee = Employee.objects.create(
        name=name,
        employee_profile=employee_profile,
        organization=organization,
        position=position,
    )
    return employee


def update_invite_employee_body(*, query: Query, data) -> Query:
    non_side_effect_fields = ['name', 'position']
    filtered_data = filter_dict_from_none_values(data)
    if query.body is None:
        raise QueryCorrupted
    query.body, has_updated = model_update(
        instance=query.body,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return query


def get_employee_profile_or_create_new_user(phone: str, email: str, name: str,
                                            organization_name: str) -> EmployeeProfile:
    user = get_user(filters={"phone": phone})
    if not user:
        with email_service():
            pwd = generate_user_password()
            subject = _("Invite to organization")
            send_message_to_new_user_with_celery.delay(
                subject,
                {'login': phone, 'password': pwd, 'organization': organization_name,
                 'name': name, 'domain': CommonConstants.OPEN_SCHOOLS_DOMAIN},
                EmailConstants.DEFAULT_FROM_EMAIL, email,
                {'phone': phone, 'user_password': pwd},
                NewUserMessageType.InviteEmployee
            )
            user = create_user(phone=phone, password=pwd, name=name, email=email)

    return user.employee_profile


def update_employee(*, employee: Employee, data) -> Employee:
    non_side_effect_fields = ['name']
    filtered_data = filter_dict_from_none_values(data)
    employee, has_updated = model_update(
        instance=employee,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return employee
