from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied

from open_schools_platform.common.selectors import selector_factory
from open_schools_platform.user_management.users.models import User, CreationToken
from open_schools_platform.user_management.users.filters import UserFilter, CreationTokenFilter
from open_schools_platform.user_management.users.services import is_token_alive


@selector_factory(User)
def get_user(*, filters=None, user: User = None, prefetch_related_list=None) -> User:
    filters = filters or {}

    qs = User.objects.all()
    retrieving_user = UserFilter(filters, qs).qs.first()

    if user and not user.has_perm('users.user_access', retrieving_user):
        raise PermissionDenied

    return retrieving_user


@selector_factory(CreationToken)
def get_token(*, filters=None, user: User = None, prefetch_related_list=None) -> CreationToken:
    filters = filters or {}

    qs = CreationToken.objects.all().order_by('created_at')
    token = CreationTokenFilter(filters, qs).qs.last()

    if user and token and not user.has_perm('users.creation_token_access', token):
        raise PermissionDenied

    return token


def get_token_with_checks(key: str, verify_check: bool = True, is_alive_check: bool = True) -> CreationToken:
    token = get_token(
        filters={"key": key},
        empty_exception=True,
    )
    if verify_check and not token.is_verified:
        raise NotAuthenticated(detail="Token is not verified.")
    if is_alive_check and not is_token_alive(token):
        raise AuthenticationFailed(detail="Token is overdue.")
    return token
