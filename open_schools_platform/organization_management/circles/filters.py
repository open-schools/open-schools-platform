from django.contrib.gis.measure import D
from django_filters import CharFilter, BooleanFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.circles.constants import CirclesConstants
from open_schools_platform.organization_management.circles.models import Circle


def circle_radius_filter(queryset, name, value):
    return queryset.filter(location__distance_lte=(value, D(km=CirclesConstants.SEARCH_RADIUS)))


class CircleFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)
    address = CharFilter(field_name="address", lookup_expr="icontains")
    organization_name = CharFilter(field_name="organization__name", lookup_expr="icontains")
    user_location = CharFilter(method=circle_radius_filter)
    name = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Circle
        fields = ("id", "organization", "capacity", "description")
