from django_filters import CharFilter
from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.parent_management.parents.models import ParentProfile


class ParentProfileFilter(BaseFilterSet):
    phone = CharFilter(field_name="user__phone")

    class Meta:
        model = ParentProfile
        fields = ('id', 'user', 'name', 'phone')
