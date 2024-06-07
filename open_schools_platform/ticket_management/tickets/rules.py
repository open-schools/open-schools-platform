import rules

from open_schools_platform.common.rules import predicate_input_type_check
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.ticket_management.tickets.models import TicketComment
from open_schools_platform.user_management.users.models import User


def ticket_sender_access():
    @rules.predicate
    @predicate_input_type_check
    def parentprofile_access(user: User, ticket: Query):
        return ticket.sender in user.parent_profile.families.all()

    return parentprofile_access


def ticket_recipient_access():
    @rules.predicate
    @predicate_input_type_check
    def organization_access(user: User, ticket: Query):
        from open_schools_platform.organization_management.organizations.selectors import get_organizations_by_user
        return ticket.recipient in get_organizations_by_user(user)

    return organization_access


@rules.predicate
@predicate_input_type_check
def ticket_comment_profile_access(user: User, ticket_comment: TicketComment):
    return user.has_perm("tickets.ticket_access", ticket_comment.ticket)


rules.add_perm("tickets.ticket_access", ticket_sender_access() | ticket_recipient_access())
rules.add_perm("tickets.ticketcomment_access", ticket_comment_profile_access)
