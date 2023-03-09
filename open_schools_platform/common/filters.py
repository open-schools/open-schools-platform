from enum import Enum
from typing import List, Type

import django_filters
from django.db.models import Q, QuerySet
from django_filters import CharFilter, BaseInFilter, UUIDFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from safedelete.config import DELETED_ONLY_VISIBLE, DELETED_VISIBLE


class SoftCondition(Enum):
    """
    This Enum determines which objects will be filtered regarding their soft deleting state
    * it is used in SafeDeleteManager.all
    """
    NOT_DELETED = None
    DELETED_ONLY = DELETED_ONLY_VISIBLE
    ALL = DELETED_VISIBLE


class CustomDjangoFilterBackend(DjangoFilterBackend):
    """
        CustomDjangoFilterBackend provide you some useful features:

        1. Generate custom filter fields with visible_filter_fields field in your view
            define dict of pairs that contain: field names and filters
    """

    def get_filterset_class(self, view, queryset=None):
        response = super().get_filterset_class(view, queryset=queryset)

        if response:
            return response

        visible_filter_fields = getattr(view, 'visible_filter_fields', None)

        if visible_filter_fields is not None:
            class AutoFilterSet(self.filterset_base):
                pass

            fields = {}

            for key, value in visible_filter_fields.items():
                fields[key] = value

            AutoFilterSet.declared_filters = fields
            AutoFilterSet.base_filters = fields

            return AutoFilterSet

        return None


class BaseFilterSet(django_filters.FilterSet):
    """
    BaseFilterSet provide you some useful features:

    1. Opportunity to use special field OR_SEARCH_FIELD that will search
    for all char fields and combine results
        * Your filter should contain this attribute: 'search = CharFilter(field_name="search", method="OR")'
        * This feature works only if your input dictionary has  pair [OR_SEARCH_FIELD: some_value]
    2. Will raise ValidationError when filter get not valid data
    3. Will order result by "-created_at" field
        * To use this class your input model type should inherit BaseModel
        otherwise you can redefine ORDER_FIELD
        * To disable this feature write ORDER_FIELD=None
        * Note: symbol '-' is the reverse trigger
    4. SoftCondition by default is NOT_DELETED
    """
    OR_SEARCH_FIELD = "search"
    ORDER_FIELD = "-created_at"

    def __init__(self, data: dict = None, queryset: QuerySet = None, **kwargs):
        self.search_value = None
        self.force_visibility = SoftCondition.NOT_DELETED
        if data is not None:
            self.force_visibility = data.get('DELETED', SoftCondition.NOT_DELETED)

        super().__init__(data, queryset, **kwargs)
        if not self.is_valid():
            raise ValidationError(self.errors)

    def OR(self, queryset, field_name, value):
        if type(value) is not str:
            raise ValidationError(detail="Search field must be str type.")

        self.search_value = value
        return queryset

    @property
    def qs(self):
        base_queryset = super().qs.all(force_visibility=self.force_visibility.value)

        if self.ORDER_FIELD:
            base_queryset = base_queryset.order_by(self.ORDER_FIELD)

        if not self.search_value:
            return base_queryset

        query = Q()
        filters = self.get_filters()
        for filter in filters.values():
            if type(filter) is CharFilter and filter.field_name != self.OR_SEARCH_FIELD:
                query |= Q(**{"{0}__icontains".format(filter.field_name): self.search_value})

        return base_queryset.filter(query)

    @staticmethod
    def get_dict_filters(filter_class: Type[django_filters.FilterSet], prefix: str = "", include: List[str] = None):
        include = include or []
        response = {}

        for key, value in filter_class.get_filters().items():
            if key in include:
                new_key = key if prefix == "" else prefix + "__" + key
                response[new_key] = value

        return response

    @staticmethod
    def get_dict_filters_without_prefix(filters):
        response = {}

        for key, value in filters.items():
            new_key = key.split("__")[1] if len(key.split("__")) > 1 else key.split("__")[0]
            response[new_key] = value

        return response


class UUIDInFilter(BaseInFilter, UUIDFilter):
    pass


def filter_by_ids(queryset, name, value):
    values = value.split(',')
    return queryset.filter(id__in=values)


def filter_by_object_ids(object_name: str):
    def func(queryset, name, value):
        values = value.split(',')
        return queryset.filter(**{"{object_name}__in".format(object_name=object_name): values})

    return func
