from open_schools_platform.parent_management.parents.filters import ParentProfileFilter
from open_schools_platform.parent_management.parents.models import ParentProfile


def get_parent_profile(*, filters=None) -> ParentProfile:
    filters = filters or {}

    qs = ParentProfile.objects.all()

    return ParentProfileFilter(filters, qs).qs.first()
