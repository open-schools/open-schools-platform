from rest_framework.exceptions import NotFound, NotAuthenticated, AuthenticationFailed

from open_schools_platform.user_management.users.models import User, CreationToken
from open_schools_platform.user_management.users.filters import UserFilter, CreationTokenFilter
from open_schools_platform.user_management.users.services import is_token_alive


def get_user(*, filters=None) -> User:
    filters = filters or {}

    qs = User.objects.all()

    return UserFilter(filters, qs).qs.first()


def get_token(*, filters=None) -> CreationToken:
    filters = filters or {}

    qs = CreationToken.objects.all().order_by('created_at')

    return CreationTokenFilter(filters, qs).qs.last()


def get_token_with_checks(key: str, verify_check: bool = True, is_alive_check: bool = True) -> CreationToken:
    token = get_token(filters={"key": key})
    if not token:
        raise NotFound(detail="No such token.")
    if verify_check and not token.is_verified:
        raise NotAuthenticated(detail="Token is not verified.")
    if is_alive_check and not is_token_alive(token):
        raise AuthenticationFailed(detail="Token is overdue.")
    return token
