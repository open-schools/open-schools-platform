from rest_framework.exceptions import PermissionDenied

from open_schools_platform.student_management.students.filters import StudentProfileFilter
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.models import User


def get_student_profile(*, filters=None, user: User = None) -> StudentProfile:
    filters = filters or {}

    qs = StudentProfile.objects.all()
    student_profile = StudentProfileFilter(filters, qs).qs.first()

    if user and student_profile and not user.has_perm('students.student_profile_access', student_profile):
        raise PermissionDenied

    return student_profile
