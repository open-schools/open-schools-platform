import re
from enum import Enum
from typing import Type

import django_filters
from django.core.exceptions import FieldError
from django.db.models import Q, QuerySet
from django_filters import CharFilter, BaseInFilter, UUIDFilter, ChoiceFilter, AllValuesFilter, OrderingFilter
from django.db.models import CharField
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
    through all filters, that are provided with it and combine results
        * Your filter should contain this attribute: 'or_search = CharFilter(field_name="or_search", method="OR")'
        * This feature works only if your input dictionary has pair [OR_SEARCH_FIELD: some_value]
    2. Will raise ValidationError when filter gets invalid data.
    The validation criteria:
        * Value passed in OR_SEARCH_FIELD should be in a strict format - value:[filter1,filter2,...]
        * Filters inside [] should:
            * exist in view's filterset
            * have CharFilter, AllValuesFilter or ChoiceFilter type
            * not have redefined method
            * not have lookup_expr that is not allowed. Allowed lookup_expressions: [i]contains, [i]exact
    3. Will order result by "-created_at" field
        * To use this class your input model type should inherit BaseModel
        otherwise you can redefine DEFAULT_ORDER_FIELD
        * To disable this feature write DEFAULT_ORDER_FIELD=None
        * Note: symbol '-' is the reverse trigger
    4. SoftCondition by default is NOT_DELETED
    """
    OR_SEARCH_FIELD = "or_search"
    DEFAULT_ORDER_FIELD = "-created_at"
    MODEL_CHARFIELD = "CharField"
    ALLOWED_FILTER_TYPES = [CharFilter, ChoiceFilter, AllValuesFilter]
    ALLOWED_LOOKUP_EXPR = ["icontains", "contains", "exact", "iexact"]

    def __init__(self, data: dict = None, queryset: QuerySet = None, **kwargs):
        self.or_search = None
        self.force_visibility = SoftCondition.NOT_DELETED
        if data is not None:
            self.force_visibility = data.get('DELETED', SoftCondition.NOT_DELETED)

        super().__init__(data, queryset, **kwargs)
        if not self.is_valid():
            raise ValidationError(self.errors)

    def OR(self, queryset, field_name, value):
        if not or_search_filter_is_valid(value):
            raise ValidationError(
                detail="or_search field must be in value:[filter1,filter2,...] format, without spaces after : sign."
            )

        self.or_search = value
        return queryset

    @property
    def qs(self):
        base_queryset = super().qs.all(force_visibility=self.force_visibility.value)

        if not self._has_provided_filter(OrderingFilter):
            base_queryset = base_queryset.order_by(self.DEFAULT_ORDER_FIELD)

        if not self.or_search:
            return base_queryset

        query = Q()
        or_search_value, or_search_filters = get_values_from_or_search(self.or_search)
        for filter_name in or_search_filters:
            try:
                filter_object = self.get_filters()[filter_name]
            except KeyError:
                raise ValidationError(detail=f"{filter_name} is not listed in this view's filters")
            exception_if_filter_is_invalid_for_or_search(filter_object, filter_name,
                                                         self.ALLOWED_FILTER_TYPES, self.ALLOWED_LOOKUP_EXPR)
            query |= Q(**{"{0}__icontains".format(filter_object.field_name): or_search_value})
        try:
            or_filtered_qs = base_queryset.filter(query)
        except FieldError:
            raise ValidationError(detail="cannot filter through this model's fields with this filter.")
        return or_filtered_qs

    def _has_provided_filter(self, filter_type: Type):
        for name, filter_field in self.get_filters().items():
            if isinstance(filter_field, filter_type) and self.data.get(name, False):
                return True
        return False


class MetaCharIContainsMixin:
    filter_overrides = {
        CharField: {
            'filter_class': django_filters.CharFilter,
            'extra': lambda f: {
                'lookup_expr': 'icontains',
            },
        },
    }


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


def or_search_filter_is_valid(value):
    pattern = re.compile(r".*?:\[[^\]]*\]", re.IGNORECASE)
    if pattern.match(value) and " " not in value.rsplit(":", 1)[1]:
        return True
    return False


def exception_if_filter_is_invalid_for_or_search(filter_object, filter_name, allowed_filter_types, allowed_lookup_expr):
    if type(filter_object) not in allowed_filter_types or filter_object.method is not None or \
            filter_object.lookup_expr not in allowed_lookup_expr:
        raise ValidationError(
            detail=f"only default (without redefined method, with [i]contains or [i]exact lookup) "
                   f"CharFilter, ChoiceFilter and AllValuesFilter are"
                   f"allowed in filters list: {filter_name} is not allowed"
        )


def get_values_from_or_search(or_search: str) -> tuple[str, list[str]]:
    or_search_list = or_search.rsplit(":", 1)
    or_search_value = or_search_list[0]
    or_search_filters = or_search_list[1].strip("][").split(",")

    return or_search_value, or_search_filters
