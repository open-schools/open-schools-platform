import rules

from open_schools_platform.common.rules import predicate_input_type_check, has_related_organization
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.user_management.users.models import User


@rules.predicate
@predicate_input_type_check
def has_circle_in_his_organizations(user: User, circle: Circle):
    return has_related_organization(user, circle.organization)


rules.add_perm("circles.circle_access", has_circle_in_his_organizations)
