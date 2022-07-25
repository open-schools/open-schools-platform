from django_filters import RangeFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.organization_management.circles.models import Circle


class CircleFilter(BaseFilterSet):
    organizations = RangeFilter(field_name='organization', lookup_expr='in')

    class Meta:
        model = Circle
        fields = ("id", "organization", "name")

