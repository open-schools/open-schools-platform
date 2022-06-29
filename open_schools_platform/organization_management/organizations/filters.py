from django_filters import RangeFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.organization_management.organizations.models import Organization


class OrganizationFilter(BaseFilterSet):
    ids = RangeFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = Organization
        fields = ["id", "name", "inn"]
