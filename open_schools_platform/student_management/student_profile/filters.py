from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.student_management.student_profile.models import StudentProfile


class StudentProfileFilter(BaseFilterSet):
    class Meta:
        model = StudentProfile
        fields = ('id', 'user', 'name', 'age')
