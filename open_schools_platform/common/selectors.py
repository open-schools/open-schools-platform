from typing import List, Any

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.contenttypes.models import ContentType
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
                return selector(filters=filters, prefetch_related_list=prefetch_related_list, **kwargs).none()
            if user:
                qs = selector(filters=filters, user=user, prefetch_related_list=prefetch_related_list, **kwargs)
            else:
                qs = selector(filters=filters, prefetch_related_list=prefetch_related_list, **kwargs)

            if empty_exception and not qs:
                raise NotFound(empty_message)
            return qs

        return wrapper

    return selector_wrapper


@selector_factory()
def generic_selector(model_name: str, object_id: str, user: User = None, **kwargs):
    ctype = ContentType.objects.get(model=model_name)
    try:
        obj = ctype.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise NotFound("sender_id is not found")

    if user and obj and not user.has_perm(f"{ctype.app_label}.{model_name}_access", obj):
        raise PermissionDenied

    return obj
