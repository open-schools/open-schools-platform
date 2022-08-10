from django.db.models import Q
from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.query_management.queries.models import Query


class QueryFilter(BaseFilterSet):
    sender_ct_search = CharFilter(field_name="sender_ct", method="sender_ct_filter")
    recipient_ct_search = CharFilter(field_name="recipient_ct", method="recipient_ct_filter")

    def sender_ct_filter(self, queryset, name, value):
        return queryset.filter(Q(sender_ct__app_label__icontains=value) |
                               Q(sender_ct__model__icontains=value.replace(" ", "")))

    def recipient_ct_filter(self, queryset, name, value):
        return queryset.filter(Q(sender_ct__app_label__icontains=value) |
                               Q(recipient_ct__model__icontains=value.replace(" ", "")))

    class Meta:
        model = Query
        fields = ('id', 'status', 'created_at', 'updated_at', 'sender_id', 'recipient_id', 'recipient_ct', 'sender_ct')
