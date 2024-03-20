import rules

from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user
from open_schools_platform.ticket_management.tickets.models import Ticket
from open_schools_platform.user_management.users.models import User


@rules.predicate
def organization_access(user: User, query: Ticket):
    return query.recipient in get_organizations_by_user(user)


@rules.predicate
def parent_profile_access(user: User, query: Ticket):
    return query.sender == user.parent_profile


rules.add_perm("tickets.ticket_access", organization_access | parent_profile_access)
