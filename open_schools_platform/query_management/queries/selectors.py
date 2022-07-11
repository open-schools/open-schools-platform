from open_schools_platform.query_management.queries.filters import QueryFilter
from open_schools_platform.query_management.queries.models import Query


def get_query(*, filters=None) -> Query:
    filters = filters or {}

    qs = Query.objects.all()

    return QueryFilter(filters, qs).qs.first()
