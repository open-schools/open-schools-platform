from open_schools_platform.common.admin import InputFilter, admin_wrapper, BaseAdmin
from django.utils.translation import gettext_lazy as _

from open_schools_platform.ticket_management.tickets.models import TicketComment, Ticket
from open_schools_platform.ticket_management.tickets.selectors import get_tickets


class SenderCTFilter(InputFilter):
    parameter_name = 'sender_ct_model'
    title = _('sender CT model')

    def queryset(self, request, queryset):
        if self.value() is not None:
            sender = self.value()

            return get_tickets(filters={"sender_ct_search": sender})


class RecipientCTFilter(InputFilter):
    parameter_name = 'recipient_ct_model'
    title = _('recipient CT model')

    def queryset(self, request, queryset):
        if self.value() is not None:
            recipient = self.value()

            return get_tickets(filters={"recipient_ct_search": recipient})


class SenderUUIDFilter(InputFilter):
    parameter_name = 'sender_uuid'
    title = _('sender UUID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            sender_uuid = self.value()

            return get_tickets(filters={'sender_id': sender_uuid})


class RecipientUUIDFilter(InputFilter):
    parameter_name = 'recipient_uuid'
    title = _('recipient UUID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            recipient_uuid = self.value()

            return get_tickets(filters={'recipient_id': recipient_uuid})


@admin_wrapper(Ticket)
class TicketAdmin(BaseAdmin):
    field_to_highlight = 'id'
    list_display = ("id", "sender_ct", "recipient_ct", "created_at", "last_comment")
    list_filter = (SenderCTFilter, SenderUUIDFilter, RecipientCTFilter, RecipientUUIDFilter)


@admin_wrapper(TicketComment)
class TicketCommentAdmin(BaseAdmin):
    field_to_highlight = 'value'
    list_display = ("is_sender", "is_seen")
    search_fields = ("value",)
    list_filter = ("is_sender", "is_seen")
