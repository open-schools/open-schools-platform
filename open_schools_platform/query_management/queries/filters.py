from typing import List

from django_filters import CharFilter

from open_schools_platform.common.filters import BaseFilterSet, filter_by_object_ids
from open_schools_platform.query_management.queries.models import Query


class QueryFilter(BaseFilterSet):
    sender_ct_search = CharFilter(field_name="sender_ct", method="sender_ct_filter")
    recipient_ct_search = CharFilter(field_name="recipient_ct", method="recipient_ct_filter")
    recipient_ids = CharFilter(method=filter_by_object_ids("recipient_id"))
    sender_ids = CharFilter(method=filter_by_object_ids("sender_id"))
    body_ids = CharFilter(method=filter_by_object_ids("body_id"))

    def sender_ct_filter(self, queryset, name, value):
        return queryset.filter(sender_ct__model=value.replace(" ", ""))

    def recipient_ct_filter(self, queryset, name, value):
        return queryset.filter(recipient_ct__model=value.replace(" ", ""))

    @staticmethod
    def get_swagger_filters(prefix: str = "", include: List[str] = []):
        if not include:
            include = ["status"]
        return BaseFilterSet.get_dict_filters(QueryFilter, prefix, include)

    class Meta:
        model = Query
        fields = ('id', 'status', 'created_at', 'updated_at', 'sender_id', 'recipient_id', 'recipient_ct', 'sender_ct')
