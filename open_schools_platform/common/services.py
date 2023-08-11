from typing import List, Dict, Any, Tuple, Callable, Type

import django_filters
from django_filters import Filter, CharFilter

from rest_framework.exceptions import ValidationError

from config.settings.email import EMAIL_TRANSPORT
from open_schools_platform.common.filters import BaseFilterSet, or_search_filter_is_valid, get_values_from_or_search
from open_schools_platform.common.types import DjangoModelType
from open_schools_platform.common.utils import get_dict_including_fields, intersect_sets, form_ids_string_from_queryset
from open_schools_platform.errors.exceptions import WrongStatusChange, QueryCorrupted, EmailServiceUnavailable, \
    ApplicationError
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.user_management.users.models import User


def model_update(
        *,
        instance: DjangoModelType,
        fields: List[str],
        data: Dict[str, Any]
) -> Tuple[DjangoModelType, bool]:
    """
    Generic update service meant to be reused in local update services

    For example:

    def user_update(*, user: User, data) -> User:
        fields = ['first_name', 'last_name']
        user, has_updated = model_update(instance=user, fields=fields, data=data)

        // Do other actions with the user here

        return user

    Return value: Tuple with the following elements:
        1. The instance we updated
        2. A boolean value representing whether we performed an update or not.
    """
    has_updated = False

    for field in fields:
        # Skip if a field is not present in the actual data
        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            has_updated = True
            setattr(instance, field, data[field])

    # Perform an update only if any of the fields was actually changed
    if has_updated:
        instance.full_clean()
        # Update only the fields that are meant to be updated.
        # Django docs reference:
        # https://docs.djangoproject.com/en/dev/ref/models/instances/#specifying-which-fields-to-save
        instance.save(update_fields=fields)

    return instance, has_updated


class BaseQueryHandler:
    """
    Base class for query handlers. It is meant to be inherited by other query handlers.
    All rules functions must use @predicate_input_type_check decorator
    Contain basic query checks

    Child class must redefine next attributes:
        allowed_statuses: list of allowed statuses

        available_statuses: a dictionary that denotes an allowed status change
            where dictionary key is tuple of (Query.Status, str) which means (actual status, required access type)
            and value is tuple of possible statuses
            example:
            available_statuses =
                {(Query.Status.SENT, 'families.family_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
                (Query.Status.SENT, 'circles.circle_access'): (Query.Status.CANCELED,)}

        change_query: a dictionary whose value is a function of query change for corresponding (key) recipient class
            example:
            def query_to_family(self, query: Query):
                ...necessary operations with query

            def query_to_teacher_profile(self, query: Query):
                ...necessary operations with query

            change_query = {
                Family: query_to_family,
                TeacherProfile: query_to_teacher_profile
            }

        without_body: a boolean value that indicates that this query type doesn't contain body
    """
    allowed_statuses: List[str] = []
    available_statuses: Dict[Tuple[str, str], Tuple] = {}
    change_query: Dict[Type, Callable[[Any, Query], Query]] = {}
    without_body = False

    def query_handler(self, query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(self, query, new_status, user, self.without_body)

        change_query_function = self.change_query.get(type(query.recipient), BaseQueryHandler.query_wrong_recipient)
        access_types = self._parse_changer_type(user, query)
        from open_schools_platform.query_management.queries.services import query_update
        for access_type in access_types:
            if (query.status, access_type) in self.available_statuses and \
                    new_status in self.available_statuses[(query.status, access_type)]:
                query_update(query=query, data={"status": new_status})
                change_query_function(self, query)
                return query

        raise WrongStatusChange(
            f'Status change [{query.status} => {new_status}] not allowed' +
            f'{", no access permissions" if len(access_types) == 0 else f" for permission {access_types}"}')

    def __call__(self, query: Query, new_status: str, user: User):
        return self.query_handler(query, new_status, user)

    def query_wrong_recipient(self, query: Query):
        raise ValidationError(
            detail=f"The recipient must one of {self.change_query.keys()}, " +
                   f"but was '{type(query.recipient).__name__}'")

    @staticmethod
    def query_handler_checks(query_handler_class, query: Query, new_status: str, user: User,
                             without_body: bool = False):
        if new_status not in query_handler_class.allowed_statuses:
            raise WrongStatusChange("Not allowed status")
        if query.status == new_status:
            raise ValidationError(detail="Identical statuses")
        if query.recipient is None or query.sender is None or without_body is False and query.body is None:
            raise QueryCorrupted()

    def _parse_changer_type(self, user: User, query: Query) -> set:
        result = set()
        required_permissions = set([key[1] for key in self.available_statuses.keys()])
        for required_permission in required_permissions:
            if user.has_perm(required_permission, query.sender):
                result.add(required_permission)
            if user.has_perm(required_permission, query.recipient):
                result.add(required_permission)
        return result


def get_object_by_id_in_field_with_checks(filters, request, fields: Dict[str, Callable[..., Any]]) \
        -> List[Any]:
    """
    Get objects by theirs ids with permission check and not found exception
    If filters don't have some keys from fields it will put None values in list in fields order

    fields should contain pairs of field name in filters and selector with selector_wrapper decorator
    """
    result = []

    for key, selector in fields.items():
        if key in filters:
            result.append(selector(
                filters={"id": filters[key]},
                user=request.user,
                empty_exception=True,
                empty_message="There is no such {key}.".format(key=key)
            ))
        else:
            result.append(None)

    return result


class SendEmailService:
    def __init__(self):
        self.email_transport = EMAIL_TRANSPORT


def exception_if_email_service_unavailable():
    if SendEmailService().email_transport is None:
        raise EmailServiceUnavailable()


def file_generate_upload_path(instance, filename):
    return f"{instance.image.name}"


class ComplexFilter:
    """
        ComplexFilter is used for filtering GenericForeignKey models and in simpler cases

        It is component that manage to convenient filter for some related model
        and return qs from specified selector

        How to configure:
            1. !!! Define ids_field in filter that selector uses and pass at initialization.
               It is necessary to merge several qs in ComplexMultipleFilter
            2. Pass selector that will filter relevant model
            3. Pass filterset where outer filters come from
            4. Pass prefix for non matching filter names in cases where several filter are used
            5. Pass including fields that will display in swagger and will be available for use
            6. Pass advance_filters for finer tuning

        How to use:
            1. Call get_dict_filters for displaying filters for clients
            2. Call get_crossed_filters for getting desired part from the complex incoming filters
            3. Call get_objects for calling selector with incoming filters
            4. Call get_ids_objects for getting ids of received qs
    """

    def __init__(self, *, filterset_type: Type[django_filters.FilterSet], selector,
                 advance_filters_delegate: Callable[[], Dict[str, Any]] = lambda: {},
                 include_list: List[str] = None, ids_field: str = None, prefix: str = None):
        self.selector = selector
        self.django_filters_list = dict(filterset_type.get_filters().items())
        self.include_list = include_list or filterset_type.get_filters().keys()
        self.ids_field = ids_field
        self.prefix = prefix
        self.advance_filters_delegate = advance_filters_delegate

    def get_dict_filters(self) -> Dict[str, Filter]:
        return {key if not self.prefix else self.prefix + "__" + key: value
                for key, value in self.django_filters_list.items() if key in self.include_list}

    def _truncate_prefix_dict_keys(self, dictionary: Dict[str, str]) -> Dict[str, str]:
        return {key.split(f"{self.prefix}__")[-1] if len(key.split(f"{self.prefix}__")) > 1 else key: value for
                key, value in
                get_dict_including_fields(dictionary, list(ComplexFilter.get_dict_filters(self).keys())).items()}

    def _truncate_prefix_list(self, _list: List[str]) -> List[str]:
        return [key.split(f"{self.prefix}__")[-1] if len(key.split(f"{self.prefix}__")) > 1 else key for
                key in intersect_sets([set(_list), set(ComplexFilter.get_dict_filters(self).keys())])]

    def get_crossed_filters(self, filters: Dict[str, str], is_or_search: bool = False) \
            -> Tuple[Dict[str, str], Dict[str, str]]:
        if is_or_search and BaseFilterSet.OR_SEARCH_FIELD in filters:
            or_search_value, or_search_list = get_values_from_or_search(filters[BaseFilterSet.OR_SEARCH_FIELD])
            new_or_search_list = self._truncate_prefix_list(or_search_list)

            if len(new_or_search_list) == 0:
                return self._truncate_prefix_dict_keys(filters), {}

            or_search_dict = {
                BaseFilterSet.OR_SEARCH_FIELD:
                    f'{or_search_value}:[{",".join(new_or_search_list)}]'
            }

            return self._truncate_prefix_dict_keys(filters), or_search_dict
        return self._truncate_prefix_dict_keys(filters), {}

    def get_objects(self, filters: Dict[str, str], empty_filter=False):
        if empty_filter and filters == {}:
            return self.selector(filters={}).none()

        return self.selector(filters=(filters | self.advance_filters_delegate()))

    def get_ids_objects(self, filters: Dict[str, str], empty_filter=False) -> str:
        return form_ids_string_from_queryset(
            self.get_objects(
                filters,
                empty_filter,
            )
        )

    def _is_root(self):
        return self.ids_field is None


class ComplexMultipleFilter(ComplexFilter):
    """
        ComplexMultipleFilter is used for filtering GenericForeignKey models

        It is class that allows to filter with several selectors defined in ComplexFilter's
        You can use ComplexMultipleFilter as ComplexFilter because of inheriting and has the same methods.

        How to configure:
            1. Pass complex_filter_list with list of ComplexFilter
            2. Pass is_has_or_search_field to enable or_search field in outer filters
            3. !!! If you use ComplexMultipleFilter object as root you don't need to use prefix and ids_field

        How to use:
            1. Call get_dict_filters for displaying filters for clients
            2. Call get_objects for calling selector with incoming filters
    """

    def __init__(self, *, complex_filter_list: List[ComplexFilter], is_has_or_search_field: bool = False, **kwargs):
        super().__init__(**kwargs)

        self.is_has_or_search_field = self._is_root() and is_has_or_search_field
        self.complex_filter_list = complex_filter_list
        self.qs_union_trigger = False
        self._preform_initialization_checks()

    def _preform_initialization_checks(self):
        prefixes = set()
        for complex_filter in self.complex_filter_list:
            if complex_filter.prefix is None:
                raise ApplicationError(message="prefix must be defined for element of complex filter list")
            if complex_filter.ids_field is None:
                raise ApplicationError(message="ids_field must be defined for element of complex filter list")

            if complex_filter.prefix in prefixes:
                raise ApplicationError(message="Elements of complex filter list must be different")
            prefixes.add(complex_filter.prefix)
            if self.is_has_or_search_field and BaseFilterSet.OR_SEARCH_FIELD not in complex_filter.django_filters_list:
                raise ApplicationError(message="All complex filters must contain or_search field if "
                                               "is_has_or_search_field targeted to True")

    def _union_condition(self, crossed_filters):
        return self.is_has_or_search_field and \
               BaseFilterSet.OR_SEARCH_FIELD in crossed_filters and \
               len(crossed_filters.keys()) == 1

    def get_objects(self, filters, empty_filters=False):
        if self.is_has_or_search_field and \
                BaseFilterSet.OR_SEARCH_FIELD in filters and \
                not or_search_filter_is_valid(filters[BaseFilterSet.OR_SEARCH_FIELD]):
            raise ValidationError(
                detail="or_search field must be in value:[filter1,filter2,...] format, without spaces after : sign."
            )

        crossed_filters = super().get_crossed_filters(
            filters, is_or_search=self.is_has_or_search_field
        )
        qs_intersection = super().get_objects(filters=crossed_filters[0])
        qs_union = super().get_objects(filters=crossed_filters[1], empty_filter=True)

        self.qs_union_trigger = False
        for complex_filter in self.complex_filter_list:
            qs_intersection, qs_union = self._complex_filter_iteration(
                filters, complex_filter, qs_intersection, qs_union
            )

        if self.qs_union_trigger:
            return qs_intersection & qs_union

        return qs_intersection

    def _complex_filter_iteration(self, filters, complex_filter: ComplexFilter, qs_intersection, qs_union):
        crossed_filters = complex_filter.get_crossed_filters(filters, is_or_search=True)
        ids_interact = complex_filter.get_ids_objects(crossed_filters[0])

        if self._union_condition(crossed_filters[1]):
            ids_union = complex_filter.get_ids_objects(crossed_filters[1], empty_filter=True)
            qs_union |= self.selector(
                filters={f'{complex_filter.ids_field}': ids_union},
                empty_filters=True
            )
            self.qs_union_trigger = True

        # TODO: optimize when crossed_filters[0] == {}
        qs_intersection &= self.selector(
            filters={f'{complex_filter.ids_field}': ids_interact},
            empty_filters=True
        )

        return qs_intersection, qs_union

    def get_dict_filters(self):
        dict_filters = super().get_dict_filters()

        if self.is_has_or_search_field:
            dict_filters |= {BaseFilterSet.OR_SEARCH_FIELD: CharFilter(field_name="or_search")}

        for i in self.complex_filter_list:
            dict_filters |= i.get_dict_filters()

        return {key if not self.prefix else self.prefix + "__" + key: value
                for key, value in dict_filters.items()}
