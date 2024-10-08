import rules

from open_schools_platform.common.rules import predicate_input_type_check
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.ticket_management.tickets.models import TicketComment
from open_schools_platform.user_management.users.models import User


@rules.predicate
@predicate_input_type_check
def ticket_sender_access(user: User, ticket: Query):
    return ticket.sender in user.parent_profile.families.all()


@rules.predicate
@predicate_input_type_check
def ticket_recipient_access(user: User, ticket: Query):
    return user.has_perm("organizations.organization_access", ticket.recipient)


@rules.predicate
@predicate_input_type_check
def ticket_comment_profile_access(user: User, ticket_comment: TicketComment):
    return user.has_perm("tickets.ticket_access", ticket_comment.ticket)


rules.add_perm("tickets.ticket_access", ticket_sender_access | ticket_recipient_access)
rules.add_perm("tickets.sender_access", ticket_sender_access)
rules.add_perm("tickets.recipient_access", ticket_recipient_access)
rules.add_perm("tickets.ticketcomment_access", ticket_comment_profile_access)
