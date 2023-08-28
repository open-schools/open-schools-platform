from typing import List, Any

from rest_framework.exceptions import NotFound

from open_schools_platform.user_management.users.models import User


def selector_factory(model=None):
    model_name = "object"
    if model:
        model_name = model.__name__.lower()

    def selector_wrapper(selector):
        def wrapper(*, filters=None, user: User = None, empty_exception: bool = False,
                    empty_message: str = f"No such {model_name}", empty_filters: bool = False,
                    prefetch_related_list: List[Any] = [], **kwargs):
            if empty_filters and any(arg in filters.values() for arg in ("", None)):
                return selector(filters=filters, prefetch_related_list=prefetch_related_list).none()
            if user:
                qs = selector(filters=filters, user=user, prefetch_related_list=prefetch_related_list)
            else:
                qs = selector(filters=filters, prefetch_related_list=prefetch_related_list)

            if empty_exception and not qs:
                raise NotFound(empty_message)
            return qs

        return wrapper

    return selector_wrapper
