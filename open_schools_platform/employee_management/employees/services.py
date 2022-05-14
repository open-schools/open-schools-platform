from open_schools_platform.employee_management.employees.models import Employee
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


def create_employee(name: str, user: User, organization: Organization, position=None) -> Employee:
    employee = Employee.objects.create(
        name=name,
        user=user,
        organization=organization,
        position=position,
    )
    return employee
