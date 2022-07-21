from rest_framework.exceptions import APIException

from open_schools_platform.organization_management.employees.models import Employee, EmployeeProfile
from open_schools_platform.organization_management.organizations.constants import OrganizationConstants
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User
from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.services import create_user, generate_user_password
from open_schools_platform.utils.sms_provider_requests import send_sms


def create_employee(name: str, position: str = "", user: User = None, organization: Organization = None) -> Employee:
    employee = Employee.objects.create(
        name=name,
        employee_profile=user.employee_profile if user is not None else None,
        organization=organization,
        position=position,
    )
    return employee


def get_employee_profile_or_create(phone: str) -> EmployeeProfile:
    user = get_user(filters={"phone": phone})

    if not user:
        pwd = generate_user_password()
        msg = OrganizationConstants.get_invite_message(phone=phone, pwd=pwd)
        response = send_sms(to=[phone], msg=msg)

        if response[str(phone)] != 100:
            raise APIException(detail="Something wrong! Please, contact the administrator"
                                      "and tell him the error number.")

        user = create_user(phone=phone, password=pwd, name="Alex Nevsky")

    return user.employee_profile


def update_employee(organization: Organization,
                    employee_profile: EmployeeProfile,
                    employee: Employee):
    employee.organization = organization
    employee.employee_profile = employee_profile
