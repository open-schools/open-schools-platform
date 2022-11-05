from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied

from open_schools_platform.common.selectors import selector_wrapper
from open_schools_platform.user_management.users.models import User, CreationToken, FirebaseNotificationToken
from open_schools_platform.user_management.users.filters import UserFilter, CreationTokenFilter, FirebaseTokenFilter
from open_schools_platform.user_management.users.services import is_token_alive


@selector_wrapper
def get_user(*, filters=None, user: User = None) -> User:
    filters = filters or {}

    qs = User.objects.all()
    retrieving_user = UserFilter(filters, qs).qs.first()

    if user and not user.has_perm('users.user_access', retrieving_user):
        raise PermissionDenied

    return retrieving_user


@selector_wrapper
def get_token(*, filters=None, user: User = None) -> CreationToken:
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
        empty_message="No such token"
    )
    if verify_check and not token.is_verified:
        raise NotAuthenticated(detail="Token is not verified.")
    if is_alive_check and not is_token_alive(token):
        raise AuthenticationFailed(detail="Token is overdue.")
    return token


def get_firebase_token_entity(*, filters=None) -> FirebaseNotificationToken:
    filters = filters or {}

    qs = FirebaseNotificationToken.objects.all().order_by('created_at')
    token = FirebaseTokenFilter(filters, qs).qs.last()

    return token
