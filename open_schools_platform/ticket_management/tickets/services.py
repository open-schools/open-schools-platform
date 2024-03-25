from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment


def create_ticket_comment(value: str, is_sender: bool, ticket: Ticket,) -> TicketComment:
    ticket_comment = TicketComment.objects.create(
        value=value,
        is_sender=is_sender,
        ticket=ticket,
    )
    return ticket_comment
