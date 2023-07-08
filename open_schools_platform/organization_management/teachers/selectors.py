from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.teachers.filters import TeacherFilter, TeacherProfileFilter
from open_schools_platform.organization_management.teachers.models import Teacher, TeacherProfile
from open_schools_platform.user_management.users.models import User


@selector_factory(Teacher)
def get_teacher(*, filters=None, user: User = None) -> Teacher:
    filters = filters or {}

    qs = Teacher.objects.all()
    teacher = TeacherFilter(filters, qs).qs.first()

    if user and teacher and not user.has_perm('teachers.teacher_access', teacher):
        raise PermissionDenied

    return teacher


@selector_factory(Teacher)
def get_teachers(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Teacher.objects.all()
    teachers = TeacherFilter(filters, qs).qs

    return teachers


@selector_factory(TeacherProfile)
def get_teacher_profile(*, filters=None, user: User = None) -> TeacherProfile:
    filters = filters or {}

    qs = TeacherProfile.objects.all()
    teacher_profile = TeacherProfileFilter(filters, qs).qs.first()

    if user and teacher_profile and not user.has_perm('teachers.teacher_profile_access', teacher_profile):
        raise PermissionDenied

    return teacher_profile


def get_teachers_from_orgaization_with_filters(organization: Organization, filters: dict) -> QuerySet:
    return TeacherFilter(filters, organization.teachers.all()).qs
