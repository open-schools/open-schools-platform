from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.organization_management.employees.selectors import get_employees
from open_schools_platform.organization_management.organizations.filters import OrganizationFilter
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.ticket_management.tickets.models import Ticket
from open_schools_platform.ticket_management.tickets.selectors import get_tickets
from open_schools_platform.user_management.users.models import User


@selector_factory(Organization)
def get_organization(*, filters=None, user: User = None, prefetch_related_list=None) -> Organization:
    filters = filters or {}

    qs = Organization.objects.all()
    organization = OrganizationFilter(filters, qs).qs.first()

    if user and organization and not user.has_perm("organizations.organization_access", organization):
        raise PermissionDenied

    return organization


@selector_factory(Organization)
def get_organizations(*, filters=None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}

    qs = Organization.objects.all()
    organizations = OrganizationFilter(filters, qs).qs

    return organizations


def get_organizations_by_user(user: User, filters: dict = {}) -> QuerySet:
    qs = get_employees(filters={"employee_profile": user.employee_profile})

    return qs if len(qs) == 0 else \
        get_organizations(filters=filters | {"ids": ','.join(list(map(lambda x: str(x.organization.id), list(qs))))})


def get_organization_circle_queries(organization: Organization):
    org_circles = organization.circles.values()
    queries = get_queries(filters={"recipient_ids": form_ids_string_from_queryset(org_circles),
                                   "sender_ct": ContentType.objects.get(model="studentprofile")},
                          empty_filters=True)
    return queries


def get_family_organization_tickets(organization: Organization) -> QuerySet[Ticket]:
    tickets = get_tickets(filters={"recipient_id": organization.id,
                                   "sender_ct": ContentType.objects.get(model="family")},
                          empty_filters=True)
    return tickets


def get_organization_students_invitations(organization: Organization):
    ...
