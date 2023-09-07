import json
from datetime import datetime
from functools import reduce

from typing import List, Dict, Any, Iterable

from dateutil.parser import parse
from django.db.models import QuerySet
from django.utils.timezone import make_aware
from requests import Response
from rest_framework import serializers

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils.http import urlencode
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.inspectors.field import get_basic_type_info


def make_mock_object(**kwargs):
    return type("", (object,), kwargs)


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
    return type(name, (serializers.Serializer,), fields)


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


def filter_list_from_empty_strings(lst: list):
    return list(filter(lambda x: x != "", lst))


def convert_str_date_to_datetime(date: str, time: str):
    """
    This function allows to convert any format date-string
    to datetime object
    """
    date = (parse(date, fuzzy=True)).strftime(f"%Y-%m-%d {time}")
    return make_aware(datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))


def reverse_querystring(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None):
    """Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})
    """
    base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if query_kwargs:
        return '{}?{}'.format(base_url, urlencode(query_kwargs))
    return base_url


def convert_qs_to_ids_set(qs: QuerySet):
    return set(map(lambda x: str(x.id), qs.all()))


def intersect_sets(lists: Iterable[set]):
    return reduce(lambda x, y: set(x) & set(y), lists)


class SwaggerSchemasGenerator:
    def __init__(self, fields: list, object_title: str, model):
        self.fields = fields
        self.object_title = object_title
        self.model = model

    def _get_field_type_info(self, field_name) -> dict:
        model_field = self.model._meta.get_field(field_name)
        field = get_basic_type_info(model_field)
        if not field:
            return {"type": openapi.TYPE_STRING, "title": str(model_field)}
        return field

    def _properties_dict_generator(self):
        for field in self.fields:
            info = self._get_field_type_info(field_name=field)
            yield {field: openapi.Schema(**info)}

    def _get_properties_dict(self):
        properties = dict()
        for property_dict in self._properties_dict_generator():
            properties |= property_dict
        return properties

    def generate_schemas(self) -> dict:
        schema = {
            "type": openapi.TYPE_OBJECT,
            "title": self.object_title,
            "properties": self._get_properties_dict(),
        }
        return schema
