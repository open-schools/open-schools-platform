from django.contrib.gis.db.models.functions import GeometryDistance
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.organization_management.circles.filters import CircleFilter
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import convert_str_to_point
from open_schools_platform.user_management.users.models import User


@selector_wrapper
def get_circles(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Circle.objects.all()
    circles = CircleFilter(filters, qs).qs
    if 'user_location' in filters:
        CircleFilter.ORDER_FIELD = None  # type: ignore
        circles = circles.order_by(GeometryDistance("location", convert_str_to_point(filters['user_location'])))
    return circles


@selector_wrapper
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
