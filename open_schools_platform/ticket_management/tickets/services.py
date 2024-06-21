from django.db.models import QuerySet, Max, Subquery
from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import generic_selector
from open_schools_platform.common.services import model_update, ComplexMultipleFilter, ComplexFilter
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.errors.exceptions import TicketIsClosed
from open_schools_platform.organization_management.organizations.filters import OrganizationFilter
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.selectors import get_organizations
from open_schools_platform.parent_management.families.filters import FamilyFilter
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.selectors import get_families
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.ticket_management.tickets.filters import TicketCommentFilter, TicketFilter
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment
from django.contrib.contenttypes.models import ContentType

from open_schools_platform.ticket_management.tickets.selectors import get_comments, get_tickets
from open_schools_platform.user_management.users.models import User


def is_ticket_available_to_change(ticket: Ticket):
    return ticket.status in [Query.Status.SENT, Query.Status.IN_PROGRESS]


def create_ticket_comment(value: str, is_sender: bool, ticket: Ticket, user: User, is_internal_recipient=False,
                          sender_ct: str = None, sender_id: str = None) -> TicketComment:
    if not is_ticket_available_to_change(ticket):
        raise TicketIsClosed()

    if (is_sender and not user.has_perm("tickets.sender_access", ticket) or
            not is_sender and not user.has_perm("tickets.recipient_access", ticket)):
        raise PermissionDenied("You can't create a comment ticket with that is_sender value.")

    if is_sender and is_internal_recipient:
        raise PermissionDenied("Sender can't create ticket comment with is_internal_recipient true value.")

    ticket_comment = TicketComment.objects.create(
        value=value,
        is_sender=is_sender,
        is_internal_recipient=is_internal_recipient,
        ticket=ticket,
        is_seen=is_internal_recipient,
    )

    if sender_id and sender_ct:
        sender = generic_selector(model_name=sender_ct, object_id=sender_id, user=user)
        ticket_comment.sender = sender
        ticket_comment.save()

    return ticket_comment


def update_ticket_comment(*, ticket_comment: TicketComment, data, user: User = None) -> TicketComment:
    is_seen = data.get('is_seen', None)

    if user and is_seen and (ticket_comment.is_sender
                             and not user.has_perm("tickets.recipient_access", ticket_comment.ticket)
                             or not ticket_comment.is_sender
                             and not user.has_perm("tickets.sender_access", ticket_comment.ticket)):
        raise PermissionDenied("You can change is_seen, it can do only your interlocutor.")

    non_side_effect_fields = ['is_seen']
    filtered_data = filter_dict_from_none_values(data)
    ticket_comment, has_updated = model_update(
        instance=ticket_comment,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return ticket_comment


def create_ticket(*, sender_model_name, recipient_model_name, **kwargs) -> Ticket:
    recipient_ct = ContentType.objects.get(model=recipient_model_name)
    sender_ct = ContentType.objects.get(model=sender_model_name)

    kwargs.update({"recipient_ct": recipient_ct})
    kwargs.update({"sender_ct": sender_ct})

    ticket = Ticket.objects.create()
    query_update(query=ticket, data=kwargs)
    return ticket


def create_family_organization_ticket(family: Family, organization: Organization) -> Ticket:
    return create_ticket(
        sender_model_name="family", sender_id=family.id,
        recipient_model_name="organization", recipient_id=organization.id,
    )


def get_family_organization_ticket_filter():
    return ComplexMultipleFilter(
        complex_filter_list=[
            ComplexFilter(
                filterset_type=FamilyFilter,
                selector=get_families,
                ids_field="sender_ids",
                prefix="family",
                include_list=["id", "name", "parent_phone"],
            ),
            ComplexFilter(
                filterset_type=OrganizationFilter,
                selector=get_organizations,
                ids_field="recipient_ids",
                prefix="organization",
                include_list=["id", "name", "inn"],
            ),
            ComplexFilter(
                filterset_type=TicketCommentFilter,
                selector=get_comments,
                ids_field="last_comment_ids",
                prefix="ticket_comment",
                include_list=["id", "value"],
            ),
        ],
        filterset_type=TicketFilter,
        selector=get_tickets,
        include_list=["status", "id", "created_at", "recipient_id", "recipient_ct", "sender_ids"],
        advance_filters_delegate=lambda: {
            "sender_ct": ContentType.objects.get(model="family"),
            "recipient_ct": ContentType.objects.get(model="organization"),
        },
        is_has_or_search_field=True,
    )


def get_last_recipient_tickets(qs: QuerySet[Ticket]) -> QuerySet[Ticket]:
    max_dates = qs.values('recipient_id').annotate(max_created_at=Max('created_at')).values('max_created_at')
    return qs.filter(
        created_at__in=Subquery(max_dates)
    )
