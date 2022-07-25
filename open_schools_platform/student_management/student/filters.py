from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.student_management.student.models import StudentProfile, Student


class StudentProfileFilter(BaseFilterSet):
    class Meta:
        model = StudentProfile
        fields = ('id', 'user', 'name', 'age')


class StudentFilter(BaseFilterSet):
    class Meta:
        model = Student
        fields = ('id', 'name', 'circles', 'student_profiles')
