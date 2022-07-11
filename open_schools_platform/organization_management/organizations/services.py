from open_schools_platform.organization_management.employees.models import EmployeeProfile, Employee
from open_schools_platform.organization_management.organizations.models import Organization


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
