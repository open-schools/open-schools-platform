import uuid

from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment
from django.contrib.contenttypes.models import ContentType


def create_ticket_comment(value: str, is_sender: bool, ticket: Ticket, ) -> TicketComment:
    ticket_comment = TicketComment.objects.create(
        value=value,
        is_sender=is_sender,
        ticket=ticket,
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
