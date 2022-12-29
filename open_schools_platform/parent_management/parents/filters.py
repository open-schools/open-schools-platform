from django_filters import CharFilter
from open_schools_platform.common.filters import BaseFilterSet, UUIDInFilter
from open_schools_platform.parent_management.parents.models import ParentProfile


class ParentProfileFilter(BaseFilterSet):
    phone = CharFilter(field_name="user__phone")
    families = UUIDInFilter(field_name="families", lookup_expr="in")

    class Meta:
        model = ParentProfile
        fields = ('id', 'user', 'name', 'phone')
