from rest_framework.exceptions import PermissionDenied, ValidationError

from open_schools_platform.organization_management.employees.models import Employee
from open_schools_platform.organization_management.employees.selectors import get_employee
from open_schools_platform.organization_management.organizations.constants import OrganizationConstants
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.services import create_user, generate_user_password
from open_schools_platform.utils.sms_provider_requests import send_sms


def create_employee(user: User, organization: Organization, name: str, position: str = "") -> Employee:
    employee = Employee.objects.create(
        name=name,
        user=user,
        organization=organization,
        position=position,
    )
    return employee


def add_employee_to_organization(user: User, phone: str,
                                 organization: Organization, name: str, position: str = "") -> Employee:
    employee = get_employee(filters={"user": user, "organization": organization})

    # TODO:implement permissions here
    if not employee:
        raise PermissionDenied()

    pwd = generate_user_password()
    add_user = get_user(filters={"phone": phone})
    if not add_user:
        msg = OrganizationConstants.get_invite_message(phone=phone, pwd=pwd)
        response = send_sms(to=[phone], msg=msg)

        if response[str(phone)] != 100:
            raise ValidationError(detail="Something wrong! Please, contact the administrator"
                                         "and tell him the error number.")

        add_user = create_user(phone=phone, password=pwd, name="Alex Nevsky")

    new_employee = create_employee(user=add_user,
                                   organization=organization,
                                   position=position,
                                   name=name)

    return new_employee
