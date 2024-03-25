from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_object_ids
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment


class TicketFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")

    sender_ct_search = CharFilter(field_name="sender_ct", method="sender_ct_filter")
    recipient_ct_search = CharFilter(field_name="recipient_ct", method="recipient_ct_filter")
    recipient_ids = CharFilter(method=filter_by_object_ids("recipient_id"))
    sender_ids = CharFilter(method=filter_by_object_ids("sender_id"))
    body_ids = CharFilter(method=filter_by_object_ids("body_id"))
    additional_ids = CharFilter(method=filter_by_object_ids("additional_id"))

    def sender_ct_filter(self, queryset, name, value):
        return queryset.filter(sender_ct__model=value.replace(" ", ""))

    def recipient_ct_filter(self, queryset, name, value):
        return queryset.filter(recipient_ct__model=value.replace(" ", ""))

    class Meta:
        model = Ticket
        fields = ('id', 'created_at', 'updated_at', 'sender_id', 'recipient_id', 'recipient_ct', 'sender_ct')


class TicketCommentFilter(BaseFilterSet):

    class Meta:
        model = TicketComment
        fields = ('id', 'created_at', 'updated_at', 'is_seen', 'is_sender', 'value', 'ticket')
