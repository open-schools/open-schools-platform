from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.selectors import generic_selector
from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment
from django.contrib.contenttypes.models import ContentType

from open_schools_platform.ticket_management.tickets.rules import \
    ticket_sender_access, ticket_recipient_access
from open_schools_platform.user_management.users.models import User


def create_ticket_comment(value: str, is_sender: bool, ticket: Ticket, user: User,
                          sender_ct: str = None, sender_id: str = None) -> TicketComment:
    if (is_sender and not ticket_sender_access()(user, ticket) or
            not is_sender and not ticket_recipient_access()(user, ticket)):
        raise PermissionDenied("You can't create a comment ticket with that is_sender value.")

    ticket_comment = TicketComment.objects.create(
        value=value,
        is_sender=is_sender,
        ticket=ticket,
    )

    if sender_id and sender_ct:
        sender = generic_selector(model_name=sender_ct, object_id=sender_id, user=user)
        ticket_comment.sender = sender
        ticket_comment.save()

    return ticket_comment


def update_ticket_comment(*, ticket_comment: TicketComment, data, user: User = None) -> TicketComment:
    is_seen = data.get('is_seen', None)

    if is_seen and (ticket_comment.is_sender and not ticket_recipient_access()(user, ticket_comment.ticket) or
                    not ticket_comment.is_sender and not ticket_sender_access()(user, ticket_comment.ticket)):
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
