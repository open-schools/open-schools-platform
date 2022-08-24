from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.organization_management.employees.selectors import get_employees
from open_schools_platform.organization_management.organizations.filters import OrganizationFilter
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


@selector_wrapper
def get_organization(*, filters=None, user: User = None) -> Organization:
    filters = filters or {}

    qs = Organization.objects.all()
    organization = OrganizationFilter(filters, qs).qs.first()

    if user and organization and not user.has_perm("organizations.organization_access", organization):
        raise PermissionDenied

    return organization


def get_organizations(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Organization.objects.all()
    organizations = OrganizationFilter(filters, qs).qs

    return organizations


def get_organizations_by_user(user: User) -> QuerySet:
    qs = get_employees(filters={"employee_profile": user.employee_profile})

    return qs if len(qs) == 0 else \
        get_organizations(filters={"ids": ','.join(list(map(lambda x: str(x.organization.id), list(qs))))})
