import json

from typing import List, Dict, Any

from django.db.models import QuerySet
from requests import Response
from rest_framework import serializers

from django.shortcuts import get_object_or_404
from django.http import Http404


def make_mock_object(**kwargs):
    return type("", (object, ), kwargs)


def get_object(model_or_queryset, **kwargs):
    """
    Reuse get_object_or_404 since the implementation supports both Model && queryset.
    Catch Http404 & return None
    """
    try:
        return get_object_or_404(model_or_queryset, **kwargs)
    except Http404:
        return None


def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer, ), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    serializer_class = create_serializer_class(name='', fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


def get_dict_from_response(response: Response):
    return json.loads(response.content.decode("utf-8"))


def get_dict_excluding_fields(dictionary: Dict[str, Any], fields: List[str]):
    return dict(filter(lambda x: x[0] not in fields, dictionary.items()))


def get_dict_including_fields(dictionary: Dict[str, Any], fields: List[str]):
    return dict(filter(lambda x: x[0] in fields, dictionary.items()))


def filter_dict_from_none_values(dictionary: Dict[str, Any]):
    return {key: value for key, value in dictionary.items() if value is not None}


def form_ids_string_from_queryset(qs: QuerySet):
    return ",".join(list(map(lambda item: str(item["id"]) if isinstance(item, dict) else str(item.id), qs)))
