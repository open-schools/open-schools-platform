from rest_framework.exceptions import PermissionDenied

from open_schools_platform.query_management.queries.filters import QueryFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.user_management.users.models import User


def get_query(*, filters=None, user: User = None) -> Query:
    filters = filters or {}

    qs = Query.objects.all()
    query = QueryFilter(filters, qs).qs.first()

    if user and query and not user.has_perm("queries.query_access", query):
        raise PermissionDenied

    return query
