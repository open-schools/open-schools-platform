from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.organization_management.circles.filters import CircleFilter, StudentQueryFilter
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.user_management.users.models import User


def get_circles(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Circle.objects.all()
    circles = CircleFilter(filters, qs).qs

    return circles


def get_circle(*, filters=None, user: User = None) -> Circle:
    filters = filters or {}

    qs = Circle.objects.all()
    circle = CircleFilter(filters, qs).qs.first()

    if user and not user.has_perm("circles.circle_access", circle):
        raise PermissionDenied

    return circle


def get_circles_by_students(students: QuerySet) -> QuerySet:
    return students if len(students) == 0 else \
        get_circles(filters={"ids": ','.join(list(map(lambda x: str(x.circle.id), list(students))))})


def get_queries_for_circle(*, filters=None, qs):
    filters = filters or {}
    queries = StudentQueryFilter(filters, qs).qs

    return queries
