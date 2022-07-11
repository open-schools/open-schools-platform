from django.contrib.contenttypes.fields import GenericForeignKey

from open_schools_platform.organization_management.organizations.models import Organization


def create_organization(name: str, inn: str) -> Organization:
    organization = Organization.objects.create(
        name=name,
        inn=inn,
    )
    return organization


def fill_employee_fields(organization: GenericForeignKey,
                         employee_profiler: GenericForeignKey,
                         employee: GenericForeignKey):
    employee.organization = organization
    employee.employee_profile = employee_profiler
