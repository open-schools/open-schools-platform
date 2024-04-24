from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied, NotFound

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.common.utils import form_ids_string_from_queryset, filter_list_from_empty_strings
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.student_management.students.filters import StudentProfileFilter, StudentFilter, \
    StudentProfileCircleAdditionalFilter
from open_schools_platform.student_management.students.models import StudentProfile, Student, \
    StudentProfileCircleAdditional
from open_schools_platform.user_management.users.models import User


@selector_factory(StudentProfile)
def get_student_profile(*, filters=None, user: User = None, prefetch_related_list=None) -> StudentProfile:
    filters = filters or {}

    qs = StudentProfile.objects.all()
    student_profile = StudentProfileFilter(filters, qs).qs.first()

    if user and student_profile and not user.has_perm('students.studentprofile_access', student_profile):
        raise PermissionDenied

    return student_profile


@selector_factory(StudentProfile)
def get_student_profiles(*, filters=None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}

    qs = StudentProfile.objects.prefetch_related(*prefetch_related_list).all()
    student_profiles = StudentProfileFilter(filters, qs).qs

    return student_profiles


@selector_factory(StudentProfileCircleAdditional)
def get_student_profiles_circle_additional(*, filters=None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}

    qs = StudentProfileCircleAdditional.objects.prefetch_related(*prefetch_related_list).all()
    objs = StudentProfileCircleAdditionalFilter(filters, qs).qs

    return objs


@selector_factory(Student)
def get_student(*, filters=None, user: User = None, prefetch_related_list=None) -> Student:
    filters = filters or {}

    qs = Student.objects.all()
    student = StudentFilter(filters, qs).qs.first()

    if user and student and not user.has_perm('students.student_access', student):
        raise PermissionDenied

    return student


@selector_factory(Student)
def get_students(*, filters=None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}

    qs = Student.objects.all()
    students = StudentFilter(filters, qs).qs

    return students


def get_student_profiles_by_families(families: QuerySet) -> QuerySet:
    if len(families) == 0:
        return families
    student_profiles_ids = \
        filter_list_from_empty_strings(
            list(map(lambda x: form_ids_string_from_queryset(x.student_profiles.all()), list(families)))
        )
    if len(student_profiles_ids) == 0:
        raise NotFound("There are no student_profiles in provided families")
    return get_student_profiles(filters={"ids": ','.join(student_profiles_ids)})


def get_student_profiles_from_family_with_filters(family: Family, filters: dict) -> QuerySet:
    return StudentProfileFilter(filters, family.student_profiles.all()).qs


def get_students_from_circle_with_filters(circle: Circle, filters: dict) -> QuerySet:
    return StudentFilter(filters, circle.students.all()).qs
