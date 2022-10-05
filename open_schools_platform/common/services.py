from typing import List, Dict, Any, Tuple, Callable

from rest_framework.exceptions import NotAcceptable, ValidationError, MethodNotAllowed

from open_schools_platform.common.types import DjangoModelType
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
    allowed_statuses: List[str] = []

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        raise NotImplementedError

    @staticmethod
    def query_handler_checks(query_handler_class, query: Query, new_status: str, user: User, without_body: bool = None):
        if new_status not in query_handler_class.allowed_statuses:
            raise NotAcceptable("Not allowed status")
        if query.status == new_status:
            raise ValidationError(detail="Identical statuses")
        if query.recipient is None or query.sender is None or without_body is None and query.body is None:
            raise MethodNotAllowed("put", detail="Query is corrupted")


def get_object_by_id_in_field_with_checks(filters, request, fields: Dict[str, Callable[..., Any]])\
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
