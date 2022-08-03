from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_ids
from open_schools_platform.organization_management.circles.models import Circle


class CircleFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)

    class Meta:
        model = Circle
        fields = ("id", "organization", "name", "address", "capacity", "description")
