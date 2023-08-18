from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, UUIDInFilter
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile


def parent_phone_filter(queryset, field_name, value):
    parent_profiles = ParentProfile.objects.prefetch_related('families') \
        .filter(user__phone__icontains=value)
    families = Family.objects.none()

    for i in parent_profiles:
        families |= i.families.all()

    return queryset & families


class FamilyFilter(BaseFilterSet):
    student_profiles = UUIDInFilter(field_name="student_profiles", lookup_expr="in")
    parent_profiles = UUIDInFilter(field_name="parent_profiles", lookup_expr="in")
    or_search = CharFilter(field_name="or_search", method="OR")
    parent_phone = CharFilter(field_name="parent_phone", method=parent_phone_filter)

    class Meta:
        model = Family
        fields = ('id', 'name', 'parent_profiles', 'student_profiles', 'parent_phone')
