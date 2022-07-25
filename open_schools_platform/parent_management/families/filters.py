from open_schools_platform.common.filters import BaseFilterSet, UUIDInFilter
from open_schools_platform.parent_management.families.models import Family


class FamilyFilter(BaseFilterSet):
    student_profiles = UUIDInFilter(field_name="student_profiles", lookup_expr="in")
    parent_profiles = UUIDInFilter(field_name="parent_profiles", lookup_expr="in")

    class Meta:
        model = Family
        fields = ('id', 'name', 'parent_profiles', 'student_profiles')
