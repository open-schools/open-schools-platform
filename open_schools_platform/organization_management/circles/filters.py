from django.contrib.gis.measure import D
from django_filters import CharFilter, BooleanFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.circles.constants import CirclesConstants
from open_schools_platform.organization_management.circles.models import Circle


class CircleFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)
    address = CharFilter(field_name="address", lookup_expr="icontains")
    organization_name = CharFilter(field_name="organization__name", lookup_expr="icontains")
    suggest_far_circles = BooleanFilter(method='circle_suggestions_filter')
    user_location = CharFilter(method='circle_radius_filter')
    name = CharFilter(field_name="name", lookup_expr="icontains")
    suggest = False

    def circle_suggestions_filter(self, queryset, name, value):
        self.suggest = value
        return queryset

    def circle_radius_filter(self, queryset, name, value):
        radius = CirclesConstants.SEARCH_RADIUS
        result = queryset.filter(location__distance_lte=(value, D(km=radius)))
        if self.suggest and len(result) == 0:
            for i in range(3):
                radius *= 10
                result = queryset.filter(location__distance_lte=(value, D(km=radius)))
                if len(result) > 0:
                    return result
        return result

    class Meta:
        model = Circle
        fields = ("id", "organization", "capacity", "description")
