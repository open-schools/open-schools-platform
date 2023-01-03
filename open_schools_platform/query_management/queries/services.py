import uuid

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from rest_framework.exceptions import MethodNotAllowed

from open_schools_platform.common.services import model_update
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_all_query_statuses
from open_schools_platform.user_management.users.models import User


def create_query(sender_model_name: str, sender_id: uuid.UUID,
                 recipient_model_name: str, recipient_id: uuid.UUID,
                 body_model_name: str = None, body_id: uuid.UUID = None,
                 additional_model_name: str = None, additional_id: uuid.UUID = None,
                 status: Query.Status = None) -> Query:
    recipient_ct = ContentType.objects.get(model=recipient_model_name)
    sender_ct = ContentType.objects.get(model=sender_model_name)

    query = Query.objects.create(recipient_ct=recipient_ct, recipient_id=recipient_id,
                                 sender_ct=sender_ct, sender_id=sender_id)

    if not (body_model_name is None or body_id is None):
        body_ct = ContentType.objects.get(model=body_model_name)
        query.body_ct = body_ct
        query.body_id = body_id

    if not (additional_model_name is None or additional_id is None):
        additional_ct = ContentType.objects.get(model=additional_model_name)
        query.additional_ct = additional_ct
        query.additional_id = additional_id

    if status is not None:
        query.status = status

    query.save()
    return query


def query_update(*, query: Query, data) -> Query:
    fields = ["status"]

    user, has_updated = model_update(
        instance=query,
        fields=fields,
        data=data
    )

    return user


def run_sender_handler(query: Query, new_status: str, user: User):
    if query.sender is None:
        raise MethodNotAllowed("put", detail="Query sender no longer exists")
    query = query.sender.query_handler(query, new_status, user)
    return query


def count_queries_by_statuses(queries: QuerySet):
    statuses = get_all_query_statuses()
    values = {}
    for status in statuses:
        filtered_qs = queries.filter(status=status)
        values[status] = filtered_qs.count()
    return values
