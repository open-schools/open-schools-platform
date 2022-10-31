import rules

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user
from open_schools_platform.user_management.users.models import User


@rules.predicate
def has_circle_in_his_organizations(user: User, circle: Circle):
    return not circle or (user and circle.organization in get_organizations_by_user(user))


rules.add_perm("circles.circle_access", has_circle_in_his_organizations)
