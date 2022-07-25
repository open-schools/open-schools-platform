from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.query_management.queries.models import Query


class QueryFilter(BaseFilterSet):
    class Meta:
        model = Query
        fields = ('id', 'status', 'created_at', 'updated_at', 'sender_id')
