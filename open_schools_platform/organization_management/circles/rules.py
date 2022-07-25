import rules

from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user
from open_schools_platform.user_management.users.models import User


@rules.predicate
def is_filtering_circles_in_common_organization(user: User, filters):
    user_organizations = get_organizations_by_user(user)
    if not user_organizations:
        return False
    return filters.get("organization") in list(map(lambda x: x.id, list(user_organizations)))


rules.add_perm("circles.circles_list_access", is_filtering_circles_in_common_organization)
