from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.parent_management.parents.filters import ParentProfileFilter
from open_schools_platform.parent_management.parents.models import ParentProfile


@selector_wrapper
def get_parent_profile(*, filters=None) -> ParentProfile:
    filters = filters or {}

    qs = ParentProfile.objects.all()

    return ParentProfileFilter(filters, qs).qs.first()
