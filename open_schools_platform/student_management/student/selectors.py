from open_schools_platform.student_management.student.filters import StudentProfileFilter
from open_schools_platform.student_management.student.models import StudentProfile


def get_student_profile(*, filters=None) -> StudentProfile:
    filters = filters or {}

    qs = StudentProfile.objects.all()

    return StudentProfileFilter(filters, qs).qs.first()
