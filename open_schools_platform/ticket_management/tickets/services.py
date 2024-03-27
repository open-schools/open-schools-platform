import uuid

from rest_framework.exceptions import PermissionDenied

from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment
from django.contrib.contenttypes.models import ContentType

from open_schools_platform.ticket_management.tickets.rules import \
    ticket_sender_access, ticket_recipient_access
from open_schools_platform.user_management.users.models import User


def create_ticket_comment(value: str, is_sender: bool, ticket: Ticket, user: User) -> TicketComment:
    if (is_sender and not ticket_sender_access()(user, ticket) or
            not is_sender and not ticket_recipient_access()(user, ticket)):
        raise PermissionDenied("You can't create a ticket with that is_sender value.")

    ticket_comment = TicketComment.objects.create(
        value=value,
        is_sender=is_sender,
        ticket=ticket,
    )
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


def create_ticket(sender_model_name: str, sender_id: uuid.UUID,
                  recipient_model_name: str, recipient_id: uuid.UUID) -> Ticket:
    recipient_ct = ContentType.objects.get(model=recipient_model_name)
    sender_ct = ContentType.objects.get(model=sender_model_name)

    ticket = Ticket.objects.create(recipient_ct=recipient_ct, recipient_id=recipient_id,
                                   sender_ct=sender_ct, sender_id=sender_id)

    return ticket


def create_parent_profile_organization_ticket(parent_profile: ParentProfile, organization: Organization) -> Ticket:
    return create_ticket(
        sender_model_name="parentprofile", sender_id=parent_profile.id,
        recipient_model_name="organization", recipient_id=organization.id,
    )
