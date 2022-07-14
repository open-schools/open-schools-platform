from rest_framework.exceptions import ValidationError

from open_schools_platform.organization_management.employees.models import EmployeeProfile, Employee
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.user_management.users.models import User


def create_organization(name: str, inn: str) -> Organization:
    organization = Organization.objects.create(
        name=name,
        inn=inn,
    )
    return organization


def update_employee(organization: Organization,
                    employee_profile: EmployeeProfile,
                    employee: Employee):
    employee.organization = organization
    employee.employee_profile = employee_profile
