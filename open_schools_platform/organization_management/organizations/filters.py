from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.organizations.models import Organization


class OrganizationFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)

    class Meta:
        model = Organization
        fields = ["id", "name", "inn"]
