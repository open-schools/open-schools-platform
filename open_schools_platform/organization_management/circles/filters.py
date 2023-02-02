from django.contrib.gis.measure import D
from django_filters import CharFilter, NumberFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.circles.constants import CirclesConstants
from open_schools_platform.organization_management.circles.models import Circle


class CircleFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)
    address = CharFilter(field_name="address", lookup_expr="icontains")
    organization_name = CharFilter(field_name="organization__name", lookup_expr="icontains")
    radius = NumberFilter(method='circle_determined_radius_filter')
    user_location = CharFilter(method='circle_radius_filter')
    name = CharFilter(field_name="name", lookup_expr="icontains")
    determined_radius = 0

    def circle_determined_radius_filter(self, queryset, name, value):
        self.determined_radius = value
        return queryset

    def circle_radius_filter(self, queryset, name, value):
        if self.determined_radius > 0:
            return queryset.filter(location__distance_lte=(value, D(km=self.determined_radius)))

        radius = CirclesConstants.START_SEARCH_RADIUS
        multiplier = CirclesConstants.RADIUS_MULTIPLIER
        count = CirclesConstants.MULTIPLICATIONS_COUNT

        result = queryset.filter(location__distance_lte=(value, D(km=radius)))
        for i in range(count):
            radius *= multiplier
            result = queryset.filter(location__distance_lte=(value, D(km=radius)))
            if len(result) > 0:
                break
        return result

    class Meta:
        model = Circle
        fields = ("id", "organization", "capacity", "description")
