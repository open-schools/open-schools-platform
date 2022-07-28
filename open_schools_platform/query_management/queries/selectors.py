from rest_framework.exceptions import PermissionDenied, NotFound, NotAcceptable

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


def get_query_with_checks(pk: str, user: User, update_query_check: bool = False) -> Query:
    query = get_query(filters={"id": pk}, user=user)
    if not query:
        raise NotFound("No such query.")
    if update_query_check:
        print(query.status)
        if query.status != Query.Status.SENT:
            raise NotAcceptable(f"Cant change query. It already has {query.status} status")
    return query


def get_queries(*, filters=None) -> Query:
    filters = filters or {}

    qs = Query.objects.all()
    queries = QueryFilter(filters, qs).qs

    return queries
