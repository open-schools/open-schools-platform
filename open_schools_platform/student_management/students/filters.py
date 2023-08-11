from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, UUIDInFilter, filter_by_ids, MetaCharIContainsMixin
from open_schools_platform.student_management.students.models import StudentProfile, Student


class StudentProfileFilter(BaseFilterSet):
    families = UUIDInFilter(field_name="families", lookup_expr="in")
    ids = CharFilter(method=filter_by_ids)
    or_search = CharFilter(field_name="or_search", method="OR")

    class Meta(MetaCharIContainsMixin):
        model = StudentProfile
        fields = ('id', 'user', 'name', 'age', 'phone', 'photo')


class StudentFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")

    class Meta(MetaCharIContainsMixin):
        model = Student
        fields = ('id', 'name', 'circle', 'student_profile', 'student_profile__phone',
                  'circle__name', 'student_profile__name', "circle__organization")
