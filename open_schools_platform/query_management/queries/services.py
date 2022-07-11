import uuid

from django.contrib.contenttypes.models import ContentType

from open_schools_platform.common.services import model_update
from open_schools_platform.query_management.queries.models import Query


# def create_query(validated_data) -> Query:
#     validated_data['recipient_ct'] = ContentType.objects.get(model=validated_data['recipient_ct']['name'])
#     validated_data['sender_ct'] = ContentType.objects.get(model=validated_data['sender_ct']['name'])
#     validated_data['body_ct'] = ContentType.objects.get(model=validated_data['body_ct']['name'])
#     query = Query.objects.create(**validated_data)
#
#     print(query.sender.name)
#     print(query.recipient.phone)
#
#     return query

def create_query(sender_model_name: str, sender_id: uuid.uuid4(),
                 recipient_model_name: str, recipient_id: uuid.uuid4(),
                 body_model_name: str, body_id: uuid.uuid4()) -> Query:
    recipient_ct = ContentType.objects.get(model=recipient_model_name)
    sender_ct = ContentType.objects.get(model=sender_model_name)
    body_ct = ContentType.objects.get(model=body_model_name)
    query = Query.objects.create(recipient_ct=recipient_ct, recipient_id=recipient_id, sender_ct=sender_ct,
                                 sender_id=sender_id, body_ct=body_ct, body_id=body_id)
    return query


def query_update(*, query: Query, data) -> Query:
    fields = ["status"]

    user, has_updated = model_update(
        instance=query,
        fields=fields,
        data=data
    )

    return user


def run_sender_handler(query: Query, new_status: str):
    query.sender.query_handler(query, new_status)

    return query
