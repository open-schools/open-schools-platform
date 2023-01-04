from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.student_management.students.filters import StudentProfileFilter, StudentFilter
from open_schools_platform.student_management.students.models import StudentProfile, Student
from open_schools_platform.user_management.users.models import User


@selector_factory(StudentProfile)
def get_student_profile(*, filters=None, user: User = None) -> StudentProfile:
    filters = filters or {}

    qs = StudentProfile.objects.all()
    student_profile = StudentProfileFilter(filters, qs).qs.first()

    if user and student_profile and not user.has_perm('students.student_profile_access', student_profile):
        raise PermissionDenied

    return student_profile


@selector_factory(StudentProfile)
def get_student_profiles(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = StudentProfile.objects.all()
    student_profiles = StudentProfileFilter(filters, qs).qs

    return student_profiles


@selector_factory(Student)
def get_student(*, filters=None, user: User = None) -> Student:
    filters = filters or {}

    qs = Student.objects.all()
    student = StudentFilter(filters, qs).qs.first()

    if user and student and not user.has_perm('students.student_access', student):
        raise PermissionDenied

    return student


@selector_factory(Student)
def get_students(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Student.objects.all()
    students = StudentFilter(filters, qs).qs

    return students


def get_student_profiles_by_families(families: QuerySet) -> QuerySet:
    return families if len(families) == 0 else \
        get_student_profiles(filters={"ids": ','.join(
            list(map(lambda x: form_ids_string_from_queryset(x.student_profiles.all()), list(families))))}
        )
