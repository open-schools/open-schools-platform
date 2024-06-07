import rules
from rules import always_deny

from open_schools_platform.user_management.users.models import User


@rules.predicate
def is_that_user(user: User, retrieving_user: User):
    return user.id == retrieving_user.id


rules.add_perm("users.user_access", is_that_user)
rules.add_perm("users.creationtoken_access", always_deny)
