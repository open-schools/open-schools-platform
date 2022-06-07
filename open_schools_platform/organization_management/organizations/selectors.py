from django.db.models import QuerySet

from open_schools_platform.organization_management.employees.selectors import get_employees
from open_schools_platform.organization_management.organizations.filters import OrganizationFilter
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


def get_organization(*, filters=None) -> Organization:
    filters = filters or {}

    qs = Organization.objects.all()

    return OrganizationFilter(filters, qs).qs.first()


def get_organizations(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Organization.objects.all()

    return OrganizationFilter(filters, qs).qs


def get_organizations_by_user(user: User) -> QuerySet:
    qs = get_employees(filters={"user": user})

    return qs if len(qs) == 0 else get_organizations(filters={"ids": list(map(lambda x: x.organization.id, list(qs)))}).order_by('id')
