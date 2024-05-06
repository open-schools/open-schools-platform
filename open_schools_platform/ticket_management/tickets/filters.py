from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_object_ids, MetaCharIContainsMixin
from open_schools_platform.ticket_management.tickets.models import Ticket, TicketComment
from django.db.models import Subquery, OuterRef


def last_comment_id(queryset, name, value):
    values = value.split(',')

    latest_comment_subquery = TicketComment.objects.filter(
        ticket_id=OuterRef('id'),
        is_internal_recipient = False
    ).order_by('-created_at').values('id')[:1]

    tickets_with_latest_comment = Ticket.objects.annotate(
        last_comment=Subquery(latest_comment_subquery)
    ) & queryset

    return tickets_with_latest_comment.filter(last_comment__in=values)


class TicketCommentFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")
    ticket_ids = CharFilter(method=filter_by_object_ids("ticket"))

    class Meta(MetaCharIContainsMixin):
        model = TicketComment
        fields = ('id', 'created_at', 'updated_at', 'is_seen', 'is_sender', 'value', 'ticket', 'is_internal_recipient')


class TicketFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")

    sender_ct_search = CharFilter(field_name="sender_ct", method="sender_ct_filter")
    recipient_ct_search = CharFilter(field_name="recipient_ct", method="recipient_ct_filter")
    recipient_ids = CharFilter(method=filter_by_object_ids("recipient_id"))
    sender_ids = CharFilter(method=filter_by_object_ids("sender_id"))
    last_comment_ids = CharFilter(method=last_comment_id)

    def sender_ct_filter(self, queryset, name, value):
        return queryset.filter(sender_ct__model=value.replace(" ", ""))

    def recipient_ct_filter(self, queryset, name, value):
        return queryset.filter(recipient_ct__model=value.replace(" ", ""))

    class Meta:
        model = Ticket
        fields = ('id', 'created_at', 'updated_at', 'sender_id', 'recipient_id', 'recipient_ct', 'sender_ct', 'status')
