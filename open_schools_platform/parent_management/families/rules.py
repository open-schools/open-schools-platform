import rules

from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.user_management.users.models import User


@rules.predicate
def is_parent_in_family(user: User, family: Family):
    return family in user.parent_profile.families.all()


rules.add_perm("families.family_access", is_parent_in_family)
