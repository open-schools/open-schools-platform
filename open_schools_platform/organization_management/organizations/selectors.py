from open_schools_platform.organization_management.organizations.filters import OrganizationFilter
from open_schools_platform.organization_management.organizations.models import Organization


def get_organization(*, filters=None) -> Organization:
    filters = filters or {}

    qs = Organization.objects.all()

    return OrganizationFilter(filters, qs).qs.first()
