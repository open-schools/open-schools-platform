from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied, NotAcceptable

from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.query_management.queries.filters import QueryFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.user_management.users.models import User


@selector_wrapper
def get_query(*, filters=None, user: User = None) -> Query:
    filters = filters or {}

    qs = Query.objects.all()
    query = QueryFilter(filters, qs).qs.first()

    if user and query and not user.has_perm("queries.query_access", query):
        raise PermissionDenied

    return query


def get_query_with_checks(pk: str, user: User, update_query_check: bool = False) -> Query:
    query = get_query(
        filters={"id": pk},
        user=user,
        empty_exception=True,
        empty_message="No such query"
    )
    if update_query_check:
        if query.status != Query.Status.SENT:
            raise NotAcceptable(f"Cant change query. It already has {query.status} status")
    return query


@selector_wrapper
def get_queries(*, filters=None) -> QuerySet:
    filters = filters or {}

    qs = Query.objects.all()
    queries = QueryFilter(filters, qs).qs

    return queries
