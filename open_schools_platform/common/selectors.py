from rest_framework.exceptions import NotFound

from open_schools_platform.user_management.users.models import User


def selector_factory(model=None):
    model_name = "object"
    if model:
        model_name = model.__name__.lower()

    def selector_wrapper(selector):
        def wrapper(*, filters=None, user: User = None, empty_exception: bool = False,
                    empty_message: str = f"No such {model_name}", **kwargs):
            if user:
                qs = selector(filters=filters, user=user)
            else:
                qs = selector(filters=filters)

            if empty_exception and not qs:
                raise NotFound(empty_message)
            return qs

        return wrapper

    return selector_wrapper
