from django.contrib.gis.db.models.functions import GeometryDistance
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.organization_management.circles.filters import CircleFilter
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import convert_str_to_point
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.user_management.users.models import User


@selector_factory(Circle)
def get_circles(*, filters=None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}

    qs = Circle.objects.prefetch_related(*prefetch_related_list).all()
    circles = CircleFilter(filters, qs).qs
    if 'user_location' in filters:
        circles = circles.order_by(GeometryDistance("location", convert_str_to_point(filters['user_location'])))
    return circles


@selector_factory(Circle)
def get_circle(*, filters=None, user: User = None, prefetch_related_list=None) -> Circle:
    filters = filters or {}

    qs = Circle.objects.prefetch_related(*prefetch_related_list).all()
    circle = CircleFilter(filters, qs).qs.first()

    if user and circle and not user.has_perm("circles.circle_access", circle):
        raise PermissionDenied

    return circle


def get_circles_by_students(students: QuerySet[Student], filters: dict = None) -> QuerySet[Circle]:
    filters = filters or {}
    return students if len(students) == 0 else \
        get_circles(filters=filters | {
            "ids": ','.join(list(map(lambda x: str(x.circle.id if x.circle else ""), list(students))))})
