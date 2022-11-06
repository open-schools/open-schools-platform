from django_filters import CharFilter, BooleanFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.organizations.models import Organization


class OrganizationFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)
    not_deleted = BooleanFilter(field_name="deleted", lookup_expr="isnull")

    class Meta:
        model = Organization
        fields = ["id", "name", "inn"]
