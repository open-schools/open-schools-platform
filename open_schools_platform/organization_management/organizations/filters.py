from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.organization_management.organizations.models import Organization


class OrganizationFilter(BaseFilterSet):
    class Meta:
        model = Organization
        fields = ('name', 'INN')
