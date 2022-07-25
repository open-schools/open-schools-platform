from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.organization_management.circles.filters import CircleFilter
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.user_management.users.models import User


def get_circles(*, filters=None, user: User = None) -> QuerySet:
    filters = filters or {}

    qs = Circle.objects.all()
    circles = CircleFilter(filters, qs).qs

    if user and not user.has_perm("circles.circles_list_access", filters):
        raise PermissionDenied

    return circles

