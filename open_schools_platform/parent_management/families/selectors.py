from open_schools_platform.parent_management.families.filters import FamilyFilter
from open_schools_platform.parent_management.families.models import Family


def get_family(*, filters=None) -> Family:
    filters = filters or {}

    qs = Family.objects.all()

    return FamilyFilter(filters, qs).qs.first()
