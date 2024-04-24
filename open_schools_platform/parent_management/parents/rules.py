import rules

from open_schools_platform.common.rules import predicate_input_type_check
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.user_management.users.models import User


@rules.predicate
@predicate_input_type_check
def is_parent_profile_owner(user: User, parent_profile: ParentProfile):
    return parent_profile.user == user


rules.add_perm("parents.parentprofile_access", is_parent_profile_owner)
