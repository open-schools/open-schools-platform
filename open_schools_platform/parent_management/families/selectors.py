from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.parent_management.families.filters import FamilyFilter
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.user_management.users.models import User


@selector_wrapper
def get_family(*, filters=None, user: User = None) -> Family:
    filters = filters or {}

    qs = Family.objects.all()
    family = FamilyFilter(filters, qs).qs.first()

    if user and family and not user.has_perm('families.family_access', family):
        raise PermissionDenied

    return family


@selector_wrapper
def get_families(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Family.objects.all()
    family = FamilyFilter(filters, qs).qs

    return family
