from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.ticket_management.tickets.filters import TicketFilter, TicketCommentFilter
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment
from open_schools_platform.ticket_management.tickets.rules import ticket_recipient_access
from open_schools_platform.user_management.users.models import User


@selector_factory(Ticket)
def get_tickets(*, filters=None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}

    qs = Ticket.objects.prefetch_related(*prefetch_related_list).all()
    tickets = TicketFilter(filters, qs).qs

    return tickets


@selector_factory(Ticket)
def get_ticket(*, filters=None, user: User = None, prefetch_related_list=None) -> Ticket:
    filters = filters or {}

    qs = Ticket.objects.all()
    ticket = TicketFilter(filters, qs).qs.first()

    if user and ticket and not user.has_perm("tickets.ticket_access", ticket):
        raise PermissionDenied

    return ticket


@selector_factory(TicketComment)
def get_comments(*, filters=None, prefetch_related_list=None) -> QuerySet:
    filters = filters or {}

    qs = TicketComment.objects.prefetch_related(*prefetch_related_list).all()
    ticket_comments = TicketCommentFilter(filters, qs).qs

    return ticket_comments.order_by('-created_at')


@selector_factory(TicketComment)
def get_comment(*, filters=None, user: User = None, prefetch_related_list=None) -> TicketComment:
    filters = filters or {}

    qs = TicketComment.objects.all()
    ticket_comment = TicketCommentFilter(filters, qs).qs.first()

    if user and ticket_comment and not user.has_perm("tickets.ticketcomment_access", ticket_comment):
        raise PermissionDenied

    return ticket_comment


def get_ticket_comments_with_user(*, ticket: Ticket, user: User):
    if ticket_recipient_access()(user, ticket):
        return get_comments(filters={'ticket': ticket})
    return get_comments(filters={'ticket': ticket, 'is_internal_recipient': False})
