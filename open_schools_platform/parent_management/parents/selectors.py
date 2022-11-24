from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.parent_management.parents.filters import ParentProfileFilter
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.user_management.users.models import User


@selector_wrapper
def get_parent_profile(*, filters=None, user: User = None) -> ParentProfile:
    filters = filters or {}

    qs = ParentProfile.objects.all()
    parent_profile = ParentProfileFilter(filters, qs).qs.first()

    if user and parent_profile and not user.has_perm('parents.parent_profile_access', parent_profile):
        raise PermissionDenied

    return parent_profile
