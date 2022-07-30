from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.parent_management.families.filters import FamilyFilter
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.user_management.users.models import User
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.student_management.students.filters import StudentProfileFilter


def get_family(*, filters=None, user: User = None) -> Family:
    filters = filters or {}

    qs = Family.objects.all()
    family = FamilyFilter(filters, qs).qs.first()

    if user and family and not user.has_perm('families.family_access', family):
        raise PermissionDenied

    return family


def get_families(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Family.objects.all()
    family = FamilyFilter(filters, qs).qs

    return family
