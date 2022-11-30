from django.db.models import QuerySet

from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.organization_management.teachers.filters import TeacherFilter
from open_schools_platform.organization_management.teachers.models import Teacher


@selector_wrapper
def get_teachers(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Teacher.objects.all()
    teachers = TeacherFilter(filters, qs).qs

    return teachers
