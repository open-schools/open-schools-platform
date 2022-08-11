from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.student_management.students.models import StudentProfile, Student


class StudentProfileFilter(BaseFilterSet):
    class Meta:
        model = StudentProfile
        fields = ('id', 'user', 'name', 'age')


class StudentFilter(BaseFilterSet):
    circle_name = CharFilter(field_name='circle__name', lookup_expr='icontains')
    student_profile_name = CharFilter(field_name='student_profile__name', lookup_expr='icontains')

    class Meta:
        model = Student
        fields = ('id', 'name', 'circle', 'student_profile')
