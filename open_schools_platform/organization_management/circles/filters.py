from django.contrib.gis.measure import D
from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.circles.constants import SEARCH_RADIUS
from open_schools_platform.organization_management.circles.models import Circle


def circle_radius_filter(queryset, name, value):
    return queryset.filter(location__distance_lte=(
        value, D(km=SEARCH_RADIUS))
    )


class CircleFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)
    address = CharFilter(field_name="address", lookup_expr="icontains")
    organization_name = CharFilter(field_name="organization__name", lookup_expr="icontains")
    user_location = CharFilter(method=circle_radius_filter)

    class Meta:
        model = Circle
        fields = ("id", "organization", "name", "capacity", "description")
